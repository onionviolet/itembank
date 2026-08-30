#!/usr/bin/env python3
"""Phase 16C (16C-08) legacy upgrade roundtrip.

Direct standard-library roundtrip script in the project's established shape:
`fail(msg)` and a non-zero exit on failure. It proves UPGRADE-01 and
UPGRADE-02 over a synthetic pre-13.5 artifact: the eleven-item audit runs
first and completely, an unavailable backing record reads the stand-in rather
than an invented pass, cosmetic and reasonless changes are never proposed, an
enhancement the artifact cannot express lands beside it with its portability
cost stated, and a keyed-meaning change halts with two affordances and no
diff.

The degraded state this file exists to prove is the halt: a change that would
move keyed assessment meaning ends the upgrade, and the artifact's bytes are
asserted unchanged on every path through this file, because a module that
writes during a dry run is a module whose review step is decorative.
"""
import ast
import hashlib
import io
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import model
import note_outputs
import upgrade_audit

LEGACY = os.path.join(ROOT, "fixtures", "legacy_pre135_bank.md")

FAILURES = []


def fail(msg):
    print("FAIL: %s" % msg)
    FAILURES.append(msg)


def _digest(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def check_fixture_parses():
    """The legacy fixture is a real, parseable, guard-clean artifact."""
    questions = model.load(LEGACY)
    if len(questions) != 2:
        fail("the legacy fixture loads %d items, expected 2"
             % len(questions))
    lesson = model.parse_lesson(LEGACY)
    if lesson is None or len(lesson["headings"]) != 3:
        fail("the legacy fixture carries %r headings, expected 3"
             % (lesson and len(lesson["headings"]),))
    if model.parse_terms(LEGACY) is not None:
        fail("the legacy fixture must carry no TERMS section; that is what "
             "makes it pre-13.5")
    text = io.open(LEGACY, encoding="utf-8").read()
    for marker in ("[[", "> [!"):
        if marker in text:
            fail("the legacy fixture carries a 13.5-era construct: %r"
                 % marker)
    run = subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "guard", ROOT],
        capture_output=True, text=True)
    if run.returncode != 0 or "0 offending files" not in run.stdout:
        fail("the legacy fixture broke guard: %r" % run.stdout[-200:])


def check_audit_first_and_complete():
    """Eleven rows, locked order, honest stand-ins."""
    rows = upgrade_audit.baseline_audit(LEGACY)
    if [r["item"] for r in rows] != list(upgrade_audit.BASELINE_AUDIT_ITEMS):
        fail("the audit rows are %r" % [r["item"] for r in rows])
    if len(rows) != 11:
        fail("the audit returned %d rows" % len(rows))
    by_item = dict((r["item"], r["result"]) for r in rows)
    for item, result in by_item.items():
        if not str(result).strip():
            fail("the %s row is empty" % item)
    for item in ("rights", "sources", "media"):
        if by_item[item] != "plan-text stand-in":
            fail("the %s row reads %r, expected the stand-in"
                 % (item, by_item[item]))
    for item in ("current_parse", "identity", "fingerprint", "validation"):
        if by_item[item] == "plan-text stand-in":
            fail("the %s row stood in for a check it could run" % item)
    if "2 items" not in by_item["current_parse"]:
        fail("the parse row is %r" % by_item["current_parse"])
    if "6c1b90ea44d24f10" not in by_item["identity"]:
        fail("the identity row does not name the item ids: %r"
             % by_item["identity"])
    if upgrade_audit.AUDIT_COMPLETION_LINE != \
            "All 11 baseline checks recorded.":
        fail("AUDIT_COMPLETION_LINE is %r"
             % (upgrade_audit.AUDIT_COMPLETION_LINE,))
    if upgrade_audit.AUDIT_HEADING != "Baseline audit":
        fail("AUDIT_HEADING is %r" % (upgrade_audit.AUDIT_HEADING,))

    # A row whose record ships later stops standing in, with no other edit.
    rows = upgrade_audit.baseline_audit(LEGACY, {"rights": True})
    by_item = dict((r["item"], r["result"]) for r in rows)
    if by_item["rights"] == "plan-text stand-in":
        fail("an available record still read the stand-in")

    # The module writes nothing.
    tree = ast.parse(io.open(os.path.join(ROOT, "upgrade_audit.py"),
                             encoding="utf-8").read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "open":
            for arg in node.args[1:]:
                if isinstance(arg, ast.Constant) and "w" in str(arg.value):
                    fail("upgrade_audit.py opens a file for writing")
            for kw in node.keywords:
                if kw.arg == "mode":
                    fail("upgrade_audit.py passes a file mode")
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        else:
            continue
        for name in names:
            if name.split(".")[0] in ("runtime", "evidence", "surfaces"):
                fail("upgrade_audit.py imports %s" % name)


def check_bounded_diff():
    """Reasoned changes are proposed; cosmetic and reasonless are not."""
    changes = [
        {"before": "states", "after": "conditions",
         "reason": "names the distinction the item actually tests"},
        {"before": "handover", "after": "hand-over", "reason": "cosmetic"},
        {"before": "spoken", "after": "verbal", "reason": ""},
    ]
    result = upgrade_audit.bounded_diff(LEGACY, changes)
    if len(result["proposed"]) != 1:
        fail("the diff proposed %d changes, expected 1"
             % len(result["proposed"]))
    if len(result["skipped"]) != 2:
        fail("the diff skipped %d changes, expected 2"
             % len(result["skipped"]))
    if result["heading"] != "Proposed changes (1)":
        fail("the diff heading is %r" % result["heading"])
    for entry in result["skipped"]:
        if entry["copy"] != "Skipped: no learning value added.":
            fail("the skip sentence is %r" % entry["copy"])
    for entry in result["proposed"]:
        for key in ("before", "after", "reason"):
            if key not in entry or not str(entry[key]).strip():
                fail("a proposed change is missing its %s" % key)
    if any(e["reason"].lower() == "cosmetic" for e in result["proposed"]):
        fail("a cosmetic change reached the proposed list")


def check_cannot_express():
    """An inexpressible enhancement lands beside the artifact, not in it."""
    before = _digest(LEGACY)
    lesson = model.parse_lesson(LEGACY)
    terms = model.parse_terms(LEGACY) or {"terms": {}, "refs": []}
    instance = note_outputs.content_instance(lesson, terms, [], [])
    result = upgrade_audit.cannot_express(LEGACY, "a concept map", instance,
                                          lesson["headings"])
    if result["copy"] != ("This artifact can't express a concept map in its "
                          "own form. It keeps its form; a derived "
                          "enhancement is linked, with its portability cost "
                          "stated."):
        fail("the cannot-express sentence is %r" % result["copy"])
    if not result["derived"].strip():
        fail("the cannot-express path produced no derived form")
    if not result["portability_cost"].strip():
        fail("the cannot-express path stated no portability cost")
    if "legacy_pre135_bank.md" not in result["portability_cost"]:
        fail("the portability cost does not name the artifact: %r"
             % result["portability_cost"])
    if _digest(LEGACY) != before:
        fail("the cannot-express path modified the artifact")


def check_identity_preserved():
    """Nothing in this module moves an item id."""
    before_text = io.open(LEGACY, encoding="utf-8").read()
    before_ids = [l for l in before_text.split("\n") if l.startswith("[ID:")]
    digest = _digest(LEGACY)

    upgrade_audit.bounded_diff(LEGACY, [{"before": "a", "after": "b",
                                         "reason": "a stated reason"}])
    lesson = model.parse_lesson(LEGACY)
    instance = note_outputs.content_instance(lesson, {"terms": {},
                                                      "refs": []}, [], [])
    upgrade_audit.cannot_express(LEGACY, "a concept map", instance,
                                 lesson["headings"])
    upgrade_audit.run_upgrade(LEGACY, [])

    after_text = io.open(LEGACY, encoding="utf-8").read()
    after_ids = [l for l in after_text.split("\n") if l.startswith("[ID:")]
    if before_ids != after_ids:
        fail("item ids moved: %r then %r" % (before_ids, after_ids))
    if not before_ids:
        fail("the fixture carries no [ID:] lines to preserve")
    if _digest(LEGACY) != digest:
        fail("the artifact's bytes changed during a read-only upgrade run")


def check_keyed_halt():
    """A keyed change halts, with two affordances and no diff."""
    digest = _digest(LEGACY)
    flipped = [{"before": "CORRECT: B\n\nWHY BEST: The spoken",
                "after": "CORRECT: A\n\nWHY BEST: The spoken",
                "reason": "a stated learning-value reason"}]
    result = upgrade_audit.run_upgrade(LEGACY, flipped)
    if not result.get("halted"):
        fail("a flipped key did not halt the upgrade")
        return
    if result["copy"] != ("Halted: this change would alter keyed assessment "
                          "meaning (keyed content). Assessment changes are "
                          "reviewed separately and are never part of an "
                          "upgrade."):
        fail("the halt sentence is %r" % result["copy"])
    if tuple(result["affordances"]) != ("Open assessment review",
                                        "Cancel upgrade"):
        fail("the halt affordances are %r" % (result["affordances"],))
    if "diff" in result:
        fail("a halted upgrade offered a diff")
    for key in result:
        if "override" in key or "force" in key:
            fail("the halted result carries an override field: %r" % key)
    if not result.get("audit"):
        fail("a halted upgrade dropped its audit rows")
    if _digest(LEGACY) != digest:
        fail("the halted run modified the artifact")

    # Difficulty and objective are keyed too.
    for change, expected in [
            ({"before": "(difficulty: application)",
              "after": "(difficulty: recall)"}, "difficulty"),
            ({"before": "[OBJECTIVE: handover / spoken summary]",
              "after": "[OBJECTIVE: handover / something else]"},
             "objective alignment")]:
        change = dict(change, reason="a stated learning-value reason")
        result = upgrade_audit.run_upgrade(LEGACY, [change])
        if not result.get("halted"):
            fail("a %s change did not halt" % expected)
        elif expected not in result["copy"]:
            fail("the %s halt names %r" % (expected, result["copy"]))


def check_prose_change_passes():
    """A rationale rewrite is not a keyed change."""
    digest = _digest(LEGACY)
    change = [{"before": "The spoken part of the invented procedure exists "
                         "for change; the",
               "after": "The spoken half of this fictional procedure carries "
                        "change, because the",
               "reason": "states the rule in the words the lesson uses"}]
    result = upgrade_audit.run_upgrade(LEGACY, change)
    if result.get("halted"):
        fail("a rationale rewrite halted: %r" % result.get("copy"))
        return
    if not result.get("audit"):
        fail("an unhalted upgrade dropped its audit rows")
    if len(result["audit"]) != 11:
        fail("the unhalted audit carried %d rows" % len(result["audit"]))
    if len(result["diff"]["proposed"]) != 1:
        fail("the prose change was not proposed: %r" % result["diff"])
    if result["completion"] != "All 11 baseline checks recorded.":
        fail("the completion line is %r" % result["completion"])
    if _digest(LEGACY) != digest:
        fail("an unhalted run modified the artifact")


def check_skill_mirrors():
    """The two skill copies stay byte-identical and describe what shipped."""
    run = subprocess.run(["diff", "-rq",
                          os.path.join(ROOT, ".agents", "skills"),
                          os.path.join(ROOT, ".claude", "skills")],
                         capture_output=True, text=True)
    if run.returncode != 0 or run.stdout.strip():
        fail("the skill mirrors diverged: %r" % run.stdout[:300])
    skill = io.open(os.path.join(ROOT, ".claude", "skills",
                                 "legacy-upgrade", "SKILL.md"),
                    encoding="utf-8").read()
    if "Stub:" in skill or "its command surface has not shipped" in skill:
        fail("the legacy-upgrade skill still describes itself as a stub")
    for name in ("upgrade_audit.baseline_audit", "upgrade_audit.run_upgrade",
                 "upgrade_audit.keyed_meaning_delta"):
        if name not in skill:
            fail("the skill does not name %s" % name)
    if "plan-text stand-in" not in skill:
        fail("the skill does not say which rows stand in")
    if chr(0x2014) in skill:
        fail("the skill contains an em dash")


def main():
    checks = [check_fixture_parses, check_audit_first_and_complete,
              check_bounded_diff, check_cannot_express,
              check_identity_preserved, check_keyed_halt,
              check_prose_change_passes, check_skill_mirrors]
    for check in checks:
        check()
    failed = len(FAILURES)
    print("LEGACY UPGRADE: %d passed, %d failed"
          % (len(checks) - failed, failed))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
