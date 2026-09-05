# 17B-03 evidence: the legacy upgrade audit (17B-CONTEXT D-05)

Recorded 2026-09-01 by plan 17B-03 Task 3, run from the repository root
with `python3` (recorded deviation, `python` not on PATH). The
`legacy-upgrade` skill is shipped (16C-08), so the audit followed
`.claude/skills/legacy-upgrade/SKILL.md` in its stated order: audit before
edit, bounded diff with a learning-value reason per change, never apply,
preserve identity, link beside what the artifact cannot express, halt on
keyed meaning. The tool proposes and writes nothing; both fixtures are
byte-identical after the run (checked below).

## The two artifacts, named

| role | artifact | why it is legacy |
|---|---|---|
| legacy lesson artifact | `fixtures/lesson_bank.md` (synthetic "Airway management" lesson bank) | a pre-16A lesson: prose under headings, no semantic callouts, no `## TERMS`, no `## MEDIA`, no `[SRC:]` locators |
| legacy question artifact | `fixtures/legacy_pre135_bank.md` (synthetic pre-13.5 shift-handover bank) | the repository's designated legacy fixture: two items with `[ID:]` and no `[HASH:]`, no `SECOND-BEST`, distractor lines that never say when they would be correct |

Both are synthetic repository fixtures, never real banks (D-02, D-05).

## The command and its script, verbatim

Invocation: `PYTHONPATH=. python3 t3_legacy_audit.py` from the repository
root. The script (transcribed in full):

```python
# 17B-03 Task 3: the D-05 legacy upgrade audit through the shipped
# legacy-upgrade contract (upgrade_audit.py, 16C). Run from the repository
# root with python3. Two synthetic repository fixtures, never real banks:
#   legacy lesson artifact:   fixtures/lesson_bank.md (a pre-16A lesson bank:
#                             prose headings, no semantic callouts, no TERMS,
#                             no MEDIA, no [SRC:] locators)
#   legacy question artifact: fixtures/legacy_pre135_bank.md (the designated
#                             pre-13.5 fixture: two items with [ID:] and no
#                             [HASH:], no SECOND-BEST, thin distractor lines)
# The tool proposes; it writes nothing. No fixture is modified by this run.
import hashlib, json
import upgrade_audit, model

LESSON = "fixtures/lesson_bank.md"
BANK = "fixtures/legacy_pre135_bank.md"

def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def show_audit(path):
    rows = upgrade_audit.baseline_audit(path)
    print(upgrade_audit.AUDIT_HEADING, "for", path)
    names = [r["item"] for r in rows]
    assert names == list(upgrade_audit.BASELINE_AUDIT_ITEMS), names
    for r in rows:
        print("  %-22s %s" % (r["item"], str(r.get("result", ""))[:120]))
    return rows

before = {LESSON: sha(LESSON), BANK: sha(BANK)}
ids_before = {p: [q.get("item_id") or q.get("id") for q in model.load(p)] for p in (LESSON, BANK)}

# 1. Baseline audit before any edit, both artifacts.
show_audit(LESSON)
show_audit(BANK)

# 2. Bounded, learning-value-stated changes for the legacy question artifact:
#    rationale-only (non-keyed) improvements the linter itself asked for.
bank_changes = [
    {"before": "- C) A page count is bookkeeping, not a handover fact.",
     "after": "- C) A page count is bookkeeping, not a handover fact; it would be correct only if the question asked what the written log's index records.",
     "reason": "the distractor now says when it WOULD be correct, so a learner who picked it learns the boundary rather than a label (lint: distractor C never says when it would be correct)"},
    {"before": "KEY DISCRIMINATOR: Whether the fact is a change or a standing condition.",
     "after": "KEY DISCRIMINATOR: Whether the fact is a change or a standing condition.\n\nSECOND-BEST: A. The inventory is the closest standing detail; it would be correct if the question asked what the written log carries.",
     "reason": "names the nearest wrong answer and the condition under which it would be right, the SECOND-BEST field the linter expects on every mc item"},
    {"before": "TRAP: Treating anything written down as unnecessary to say aloud.",
     "after": "TRAP: Treating anything written down as unnecessary to say aloud.",
     "reason": "cosmetic"},
]
diff = upgrade_audit.bounded_diff(BANK, bank_changes)
print(diff["heading"], "for", diff["path"])
for c in diff["proposed"]:
    print("  proposed: reason=%r" % c["reason"][:90])
for c in diff["skipped"]:
    print("  skipped:  %s (reason was %r)" % (c["copy"], c["reason"]))

# 3. The whole upgrade in the only order allowed: audit, compare, propose.
run = upgrade_audit.run_upgrade(BANK, bank_changes)
print("run_upgrade (rationale-only changes): halted=%s, proposed=%d, completion=%r"
      % (run.get("halted"), len((run.get("diff") or {}).get("proposed", [])), run.get("completion")))
print("  result keys:", sorted(run.keys()))
for c in run["diff"]["proposed"]:
    print("  --- before ---"); print("  " + c["before"].replace("\n", "\n  "))
    print("  --- after ----"); print("  " + c["after"].replace("\n", "\n  "))
    print("  --- reason ---"); print("  " + c["reason"])

# 4. The halt: a stem rewrite is keyed meaning and must halt with exactly two affordances.
keyed = [{"before": "Q2. Which handover sentence follows the procedure in this fixture?",
          "after": "Q2. Which handover sentence violates the procedure in this fixture?",
          "reason": "sharper stem (this is a keyed change and must halt)"}]
halt = upgrade_audit.run_upgrade(BANK, keyed)
print("run_upgrade (stem rewrite): halted=%s" % halt.get("halted"))
print("  copy:", halt.get("copy"))
print("  affordances:", halt.get("affordances"), "| diff present:", "diff" in halt and bool(halt.get("diff")))

# 5. The legacy lesson artifact: what it cannot express is linked beside it,
#    with the portability cost said out loud (semantic callouts and term
#    registries exist in 16A's grammar; a pre-16A lesson bank carries prose only).
import note_outputs
les = model.parse_lesson(LESSON)
terms = model.parse_terms(LESSON) or {"terms": {}, "refs": []}
instance = note_outputs.content_instance(les, terms, [], [])
headings = les["headings"]
cannot = upgrade_audit.cannot_express(
    LESSON, "semantic teaching roles (things-to-know, expert tip) and a term registry",
    instance, headings)
print("cannot_express:", cannot["copy"])
print("  derived_ok=%s; portability cost: %s" % (cannot["derived_ok"], cannot["portability_cost"]))
print("  derived projection head:", cannot["derived"].strip().splitlines()[0] if cannot["derived"] else "")

# 6. Nothing written; identity preserved.
after = {LESSON: sha(LESSON), BANK: sha(BANK)}
ids_after = {p: [q.get("item_id") or q.get("id") for q in model.load(p)] for p in (LESSON, BANK)}
print("fixture bytes unchanged:", before == after, "| item ids unchanged:", ids_before == ids_after)
print("ids:", json.dumps(ids_after))
```

## Output, verbatim

```
Baseline audit for fixtures/lesson_bank.md
  current_parse          3 items, 2 lesson headings
  identity               q1, q2, q3
  fingerprint            sha256:fdb92febb303424c, sha256:50c4a4a02c13486d, sha256:fe930f3f39f98aaf
  objectives             3 of 3 items carry an objective
  sources                plan-text stand-in
  rights                 plan-text stand-in
  media                  plan-text stand-in
  assessment_boundaries  2 keyed items
  plain_rendering        6386 characters, first line '# Airway management (synthetic)'
  rich_rendering         2 headings the reader can render
  validation             0 errors, 3 warnings
Baseline audit for fixtures/legacy_pre135_bank.md
  current_parse          2 items, 3 lesson headings
  identity               6c1b90ea44d24f10, 91f7a2cd58b34e07
  fingerprint            sha256:e679e638b49fbdc9, sha256:334524f474d9f985
  objectives             2 of 2 items carry an objective
  sources                plan-text stand-in
  rights                 plan-text stand-in
  media                  plan-text stand-in
  assessment_boundaries  2 keyed items
  plain_rendering        3109 characters, first line '# Fictional pre-13.5 shift-handover bank (synthetic legacy f'
  rich_rendering         3 headings the reader can render
  validation             0 errors, 9 warnings
Proposed changes (2) for legacy_pre135_bank.md
  proposed: reason='the distractor now says when it WOULD be correct, so a learner who picked it learns the bo'
  proposed: reason='names the nearest wrong answer and the condition under which it would be right, the SECOND'
  skipped:  Skipped: no learning value added. (reason was 'cosmetic')
run_upgrade (rationale-only changes): halted=False, proposed=2, completion='All 11 baseline checks recorded.'
  result keys: ['audit', 'completion', 'diff', 'halted']
  --- before ---
  - C) A page count is bookkeeping, not a handover fact.
  --- after ----
  - C) A page count is bookkeeping, not a handover fact; it would be correct only if the question asked what the written log's index records.
  --- reason ---
  the distractor now says when it WOULD be correct, so a learner who picked it learns the boundary rather than a label (lint: distractor C never says when it would be correct)
  --- before ---
  KEY DISCRIMINATOR: Whether the fact is a change or a standing condition.
  --- after ----
  KEY DISCRIMINATOR: Whether the fact is a change or a standing condition.

  SECOND-BEST: A. The inventory is the closest standing detail; it would be correct if the question asked what the written log carries.
  --- reason ---
  names the nearest wrong answer and the condition under which it would be right, the SECOND-BEST field the linter expects on every mc item
run_upgrade (stem rewrite): halted=True
  copy: Halted: this change would alter keyed assessment meaning (keyed content). Assessment changes are reviewed separately and are never part of an upgrade.
  affordances: ('Open assessment review', 'Cancel upgrade') | diff present: False
cannot_express: This artifact can't express semantic teaching roles (things-to-know, expert tip) and a term registry in its own form. It keeps its form; a derived enhancement is linked, with its portability cost stated.
  derived_ok=True; portability cost: The derived form lives beside lesson_bank.md, not inside it, so copying or exporting the artifact alone leaves the enhancement behind.
  derived projection head: # Concept map
fixture bytes unchanged: True | item ids unchanged: True
ids: {"fixtures/lesson_bank.md": ["q1", "q2", "q3"], "fixtures/legacy_pre135_bank.md": ["6c1b90ea44d24f10", "91f7a2cd58b34e07"]}
```

The verify command for the audited bank, verbatim:

```
$ python3 itembank.py lint fixtures/legacy_pre135_bank.md
2 items, 0 errors, 12 warnings
exit=0
```

(and for the lesson artifact, `python3 itembank.py lint
fixtures/lesson_bank.md`: `3 items, 0 errors, 4 warnings`, exit 0.)

## The five D-05 checks, each with its outcome

| D-05 check | outcome | where in the output |
|---|---|---|
| 1. Baseline audit before edit | pass: all eleven rows in the frozen order for both artifacts, `All 11 baseline checks recorded.`; `sources`, `rights`, `media` read `plan-text stand-in`, reported as such and not filled in by the agent (the skill's own instruction) | the two `Baseline audit for ...` blocks |
| 2. Learning-value delta stated | pass: every proposed change carries a `reason` naming what it teaches better; the one `cosmetic` change was refused with `Skipped: no learning value added.` and never reached the proposed list | `Proposed changes (2)`, the `skipped` line |
| 3. Identity and assessment meaning preserved | pass: item ids identical before and after (`6c1b90ea44d24f10, 91f7a2cd58b34e07`; `q1, q2, q3`); fingerprints unchanged by rationale-only edits (`keyed_meaning_delta` empty, `halted=False`); the stem rewrite halted with the frozen `KEYED_HALT_COPY` and exactly the two affordances `Open assessment review` and `Cancel upgrade`, no diff and no override | `run_upgrade (rationale-only ...)`, `run_upgrade (stem rewrite)`, `item ids unchanged: True` |
| 4. Bounded diff presented | pass: two `before`/`after`/`reason` triples, each a single rationale line of one item, presented for human review and NOT applied (`fixture bytes unchanged: True`); the write path would be the 14A journal operations under the operation contract, not this tool | the `--- before --- / --- after ---` blocks |
| 5. Static and accessibility fallbacks retained | pass: no proposed change touches the lesson prose, a heading, or an option; the legacy lesson keeps its form and the enhancement it cannot express (16A semantic roles and a term registry) is linked beside it as a derived projection with the portability cost stated in words | `cannot_express`, `portability cost` |

## Verdicts

- `fixtures/legacy_pre135_bank.md` (legacy question artifact): auditable,
  upgradeable by the two rationale-only changes above once a human
  accepts the diff; the stem rewrite is correctly refused as keyed
  meaning. Nothing was written.
- `fixtures/lesson_bank.md` (legacy lesson artifact): auditable; its
  missing 16A capabilities cannot be expressed in its own form and are
  linked beside it with the portability cost stated. Nothing was written.
- Skill state: shipped, not a stub; no skill gap to record under D-06.
  The three `plan-text stand-in` rows remain the honest answer the 16C
  freeze already carries as an open item (owner: whichever phase ships
  the sources, rights, and media records).

## Egress record (17B-CONTEXT D-09)

No hosted-model call; module calls over local files only.
