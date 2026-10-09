"""Internal runtime component; public access goes through runtime."""
import re


def answer_text(q):
    """Compact answer text for study and export surfaces."""
    import runtime
    if q["type"] in ("mc", "multi"):
        return "; ".join("%s) %s" % (c, q["opts"][c]) for c in q["correct"])
    if q["type"] in ("table", "dnd"):
        labels = {c["id"]: c["text"] + " (" + c["id"] + ")" for c in (q.get("matching") or {}).get("choices", [])}
        return "; ".join("%s -> %s" % (r["text"], labels.get(r["cat"], r["cat"])) for r in q["rows"])
    if q["type"] == "build":
        if "ordering" in q:
            texts = {b["id"]: b["text"] for b in q["blocks"]}
            return "One valid order: " + " -> ".join(texts[i] for i in runtime.ordering_example(q))
        return " -> ".join(q["steps"])
    if q["type"] == "fill":
        return "\n".join("%s: %s" % (
            field["label"], " / ".join(field["accepted"]) if field["kind"] == "text"
            else field["checker"]["target"] if field["kind"] == "polynomial"
            else field["answer"] + (" " + field["unit"] if field.get("unit") else ""))
            for field in q.get("fields") or [])
    if q["type"] == "check":
        # No keyed option and no model answer; describe what the item asks in
        # the same terse voice the other branches use. Never the case inputs
        # or expected outputs -- this feeds surfaces that show an answer
        # before the learner has attempted the item (plan 05-07).
        n = len(q.get("cases") or [])
        return "code check: %d hidden test case%s (%s)" % (
            n, "" if n == 1 else "s", q.get("lang") or "python")
    return q.get("model", "")


def glossable(qs, term):
    """The one gate between a term's definition and the learner: False when
    the definition text could disclose keyed answer material from any
    question in `qs`, True otherwise.

    This is the same class of decision as `public_item()` withholding a key:
    the runtime, not the author and not a model, decides what reaches the
    learner (Directive §4.1, D-20). It is deliberately conservative -- on any
    ambiguity it returns False. It is a pure function: no I/O, no side
    effects, deterministic across calls. It is NOT a secrecy mechanism
    against the file on disk: the learner owns the bank markdown, and
    UI-SPEC §8.4 states that plainly.

    The answer-bearing fragments are the fields `public_item()` WITHHOLDS:
    the correct option labels, the canonical key output of `canonical_key()`,
    the collapsed key/answer text for short and build items, and, added
    2026-08-28, the authored rationale block (`WHY BEST`, `KEY DISCRIMINATOR`,
    `SECOND-BEST`, and each `DISTRACTOR ANALYSIS` line).

    Deriving the fragment set from what `public_item` withholds makes the two
    gates agree BY CONSTRUCTION rather than by coincidence. Before the
    rationale was added they disagreed: `public_item` withheld `WHY BEST` and
    `glossable` admitted a definition quoting it verbatim, so an author could
    reproduce the rationale into a term definition or a source excerpt and no
    gate saw it. Rationale fragments are whole sentences, so this catches
    verbatim reproduction and not incidental word overlap, which is exactly
    the sensitivity wanted: quoting a rationale is a disclosure, sharing a
    noun with one is not.

    **How a fragment is matched, and why it is not a bare substring
    (corrected 2026-08-28).** A multi-character fragment must appear on word
    boundaries, so a definition is refused for containing the option text
    "two" but not for containing "twofold". A SINGLE-CHARACTER fragment, which
    in practice is a multiple-choice item's option letter, must additionally
    appear as a capital letter that is not opening a sentence.

    That last rule exists because the previous bare-substring test made this
    gate useless. `canonical_key()` for a multiple-choice item returns the
    bare correct option letter, so a bank keyed `A` refused every definition
    containing the letter "a", which is every definition anyone would write:
    both terms in `fixtures/terms_above_lesson_bank.md` were suppressed, and
    the hover, focus, and touch glossary was effectively off in any bank with
    a multiple-choice item. A gate that refuses everything is not a
    conservative gate; it is a disabled feature that looks like a gate.

    The rule distinguishes the two ways a single letter appears in English:
    "The keyed letter is B, placed with the stem" names a letter and is
    refused, while "A small invented thing" opens with an article and is
    admitted. It reads the ORIGINAL definition for case, not the collapsed
    one, because case is the whole signal.

    This loosening is bounded and deliberate. Per UI-SPEC section 8.4 this
    gate is NOT a secrecy mechanism against the file on disk: the learner owns
    the bank markdown and can read the key there. It exists so a definition
    does not hand over an answer mid-sitting, and every fragment that actually
    carries the answer, the option text, the model answer, the build steps,
    and every multi-character canonical key, is still matched.
    """
    import runtime
    def _collapse(s):
        return " ".join(str(s or "").split()).lower()

    raw_definition = " ".join(str(term.get("def") or "").split())
    definition = raw_definition.lower()
    if not definition:
        return True
    for q in qs:
        t = q["type"]
        if t in ("mc", "multi"):
            frags = [q["opts"][c] for c in q["correct"]]
        elif t == "fill":
            frags = []
            for field in q.get("fields") or []:
                if field.get("kind") in ("numeric", "polynomial"):
                    # A tolerance interval and converted quantities have many
                    # equivalent spellings. Free prose cannot be proven free
                    # of these answers by matching a finite fragment list.
                    return False
                candidate = runtime._fill_text(field, raw_definition)
                for accepted in field.get("accepted") or []:
                    fragment = runtime._fill_text(field, accepted)
                    if fragment and fragment in candidate:
                        return False
                frags.extend(field.get("accepted") or [])
            # A one-character typed key is content, not an MC option label.
            # Retain the conservative substring check for this form.
            if any(_collapse(frag) in definition for frag in frags if _collapse(frag)):
                return False
        elif t == "short":
            frags = [q.get("model", "")]
        elif t == "build":
            frags = list(q.get("steps") or [])
        else:
            frags = []
        key = runtime.canonical_key(q)
        if key is not None:
            frags.append(key)
        # The authored rationale block: every field `public_item()` withholds
        # and `explain_payload()` releases only after a response exists.
        frags.append(q.get("why") or "")
        frags.append(q.get("disc") or "")
        frags.append(q.get("second") or "")
        frags.extend((q.get("da") or {}).values())
        for frag in frags:
            frag = _collapse(frag)
            if not frag:
                continue
            if runtime._fragment_discloses(definition, raw_definition, frag):
                return False
    return True


_GLOSS_WORD_RE = re.compile(r"[0-9a-z]")


def _fragment_discloses(definition, raw_definition, frag):
    """True when `frag` appears in `definition` as a real occurrence rather
    than as a coincidence inside a longer word.

    Split out of `glossable` so the single-character rule has one home and one
    docstring rather than being an inline branch nobody can find. `definition`
    is lowercased and collapsed; `raw_definition` is the same text with its
    original case, which the single-character rule reads.
    """
    import runtime
    start = 0
    while True:
        at = definition.find(frag, start)
        if at == -1:
            return False
        end = at + len(frag)
        before = definition[at - 1] if at else ""
        after = definition[end] if end < len(definition) else ""
        embedded = bool(runtime._GLOSS_WORD_RE.fullmatch(before)) \
            or bool(runtime._GLOSS_WORD_RE.fullmatch(after))
        if not embedded:
            if len(frag) > 1:
                return True
            # A single character, which in practice is an option letter. It
            # discloses only when it is NAMING a letter, which in English
            # means a capital that is not opening a sentence. An article or a
            # sentence-initial capital is not a disclosure.
            original = raw_definition[at:end]
            if original.isupper():
                preceding = raw_definition[:at].rstrip()
                sentence_initial = (not preceding
                                    or preceding[-1] in ".!?:;")
                if not sentence_initial:
                    return True
        start = at + 1
