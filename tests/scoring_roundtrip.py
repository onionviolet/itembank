#!/usr/bin/env python3
"""Assert there is one scorer, and that the offline page cannot become a second.

`build` writes a file:// page with no process behind it, so it has to be able to
self-check. It does that by carrying a canonical key that Python computed and
comparing one string against it, which is a lookup rather than a second set of
scoring rules. That only holds while the key it carries is the same value the
scorer compares against, so this asserts it directly.

Standard library only, runnable as `python tests/scoring_roundtrip.py`.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                            # noqa: E402

BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def correct_answer(q):
    if q["type"] == "mc":
        return q["correct"][0]
    if q["type"] == "multi":
        return list(q["correct"])
    if q["type"] in ("table", "dnd"):
        return dict((str(i), r["cat"]) for i, r in enumerate(q["rows"]))
    if q["type"] == "build":
        return list(q["steps"])
    return "A constructed response."


def wrong_answers(q):
    """Every way of being wrong that has bitten a scorer here before."""
    if q["type"] == "mc":
        return [next(k for k in sorted(q["opts"]) if k != q["correct"][0]), "", []]
    if q["type"] == "multi":
        others = [k for k in sorted(q["opts"]) if k not in q["correct"]]
        return [others[:len(q["correct"])], list(q["correct"])[:-1],
                list(q["correct"]) + others[:1]]
    if q["type"] in ("table", "dnd"):
        right = dict((str(i), r["cat"]) for i, r in enumerate(q["rows"]))
        swapped = dict(right)
        swapped["0"] = next(c for c in q["cats"] if c != right["0"])
        short = dict((k, v) for k, v in list(right.items())[:-1])
        padded = dict(right)
        padded["99"] = q["cats"][0]
        return [swapped, short, padded, []]
    if q["type"] == "build":
        return [list(reversed(q["steps"])), q["steps"][:-1], "not a list"]
    return []


def main():
    qs = itembank.parse_bank(open(BANK, encoding="utf-8").read())
    if not qs:
        fail("fixture bank parsed to nothing")

    for q in qs:
        want = None if q["type"] == "short" else True
        got = itembank.score_response(q, correct_answer(q))
        if got is not want:
            fail("%s (%s): the correct response scored %r" % (q["id"], q["type"], got))
        for bad in wrong_answers(q):
            if itembank.score_response(q, bad) is not False:
                fail("%s (%s): %r was not marked wrong" % (q["id"], q["type"], bad))

        # The static page's key and the scorer's key are the same value, or the
        # offline surface silently disagrees with every other one.
        item = itembank.page_item(q, reveal=True, offline=True)
        if item["key"] != itembank.canonical_key(q):
            fail("%s: the offline page key differs from the scorer's key" % q["id"])
        if q["type"] != "short" and \
                itembank.canonical_response(q, correct_answer(q)) != item["key"]:
            fail("%s: the canonical response of a correct answer is not the key" % q["id"])

        # And the served shape carries neither.
        public = itembank.page_item(q, offline=False)
        for leak in ("key", "explain", "correct", "opts", "cats", "da", "why", "model"):
            if leak in public:
                fail("%s: the served item shape carries %r" % (q["id"], leak))

    # Separators have to survive content that contains punctuation, which is the
    # reason they are control characters rather than "|" or ">".
    tricky = {"type": "build", "steps": ["a > b", "c | d", "e , f"]}
    if itembank.score_response(tricky, ["a > b", "c | d", "e , f"]) is not True:
        fail("a build item whose steps contain separators scored wrong")
    if itembank.score_response(tricky, ["a", "> b", "c | d", "e , f"]) is not False:
        fail("a build item was scored right on a different step list")

    # One scorer, structurally, across every module rather than in the one file
    # that happens to hold it today.
    scorers = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "tests")]
        for f in sorted(files):
            if not f.endswith(".py"):
                continue
            path = os.path.join(base, f)
            source = open(path, encoding="utf-8").read()
            scorers += [(os.path.relpath(path, ROOT), n)
                        for n in re.findall(r"(?m)^def (\w*score\w*)\(", source)]
    if scorers != [("runtime.py", "score_response")]:
        fail("expected exactly one scorer, found %r" % (scorers,))

    # T-R4-01 (plan 05-01): score_response is byte-identical after the
    # registry conversion, pinned by source hash. Any later phase editing the
    # scorer fails this named test and must argue for it in a plan rather than
    # in a diff. Recorded against the final post-guard source. Re-pinned on
    # the main merge: phase 06.1's visual branch entered the sole scorer (the
    # visual verdict is special-cased before the canonical comparison), while
    # phase 05's check behaviour -- a None canonical is never a False verdict
    # (timeout) -- is preserved below it.
    import hashlib, inspect
    pinned = "7471f61b39d25c77090bd81b6ca5f2f42e2c7f921068097b203ffdd934be3514"
    src = inspect.getsource(itembank.score_response)
    if hashlib.sha256(src.encode("utf-8")).hexdigest() != pinned:
        fail("T-R4-01: runtime.score_response drifted from its pinned source "
             "(hash %s)" % hashlib.sha256(src.encode("utf-8")).hexdigest())

    print("scoring contract: ok (%d items, one scorer)" % len(qs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
