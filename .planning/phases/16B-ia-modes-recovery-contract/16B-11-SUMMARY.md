# 16B-11 summary

Plan `16B-11`, wave 11, three tasks, all complete. Phase 16B is frozen.

## Command output

| Command | Final line |
|---|---|
| `python3 tests/ia_route_roundtrip.py` | `IA ROUTES: 24 passed, 0 failed` |
| `python3 tests/ia_storyboard_tracer.py` | `STORYBOARD: 12 passed, 0 skipped, 0 failed` |
| `python3 tests/mode_layer_roundtrip.py` | `MODE LAYERS: 6 passed, 0 failed` |
| `python3 tests/degraded_state_roundtrip.py` | `DEGRADED: 7 passed, 0 failed` |
| `python3 tests/daemon_roundtrip.py` | exit 0 |
| `python3 tests/config_roundtrip.py` | exit 0 |
| `python3 tests/theme_roundtrip.py` | exit 0 |
| the full suite, 88 files | `0 failing` |
| `python3 itembank.py guard .` | `0 offending files` |
| `git status --porcelain` | no `_sample_course` and no `_ia` entry |
| the freeze-record shape check | `freeze record shape ok: frozen` |

## The six freeze legs

| Leg | Result |
|---|---|
| All four new 16B suites green with zero failures | holds |
| Full suite green and `guard` reporting `0 offending files` | holds, after the fix recorded below |
| Settings additivity unchanged for every pre-existing key | holds, byte-identical |
| `16B-REVIEW.md` exists, signed, verdict `accept` or `accept-with-findings` | holds, `accept-with-findings` under standing delegation |
| `16B-PRECONDITION.md`'s Deviations resolved | holds, both recorded deviations resolved in phase summaries |
| Every `SKIPPED` stage carries a recorded judgment | holds vacuously, zero skipped stages |

## Leg 2 was failing when Task 1 ran, and the failure was fixed rather than judged

Task 1's measured pass found the full suite red:
`tests/retention_roundtrip.py` failing with `3 settled with 1 correct must be
weak, got 'at-risk'`, and `tests/phase_062_audit.py` inheriting it.

Diagnosed as an expiring fixture, not a 16B regression. Two `report()` calls in
`check_states` omitted the fixed `cutoff` that every other case in the file
passes, so they read the wall clock while their events stayed pinned to August
2026. Once real elapsed time passed `at_risk_after_days` (28), at-risk won the
D-14 precedence order and the assertion failed on a tree nobody had changed.
Verified pre-existing by reproducing it on a detached `git worktree` at `HEAD`.

Weibao was given three options: fix the fixture, freeze anyway with the failure
recorded as an open item, or withhold the freeze. He chose to fix it. Both calls
now pass `cutoff="2026-08-10T12:00:00.000Z"`, so the fixture cannot age out
again, and the second call (`base3`, the mastered case) was pinned too because
it would have expired within two days for the same reason. The suite is now
genuinely green and the freeze rests on a green tree.

This is a change outside 16B's scope, made under an explicit instruction, and it
is recorded in the freeze record's open items as well as here.

## The review leg closed under standing delegation

Weibao was offered three ways to handle the blocking contract-legibility review:
perform it himself, sign an agent-drafted review, or delegate outright. He chose
to delegate outright.

`16B-REVIEW.md` therefore records `accept-with-findings`, labelled in its
Provenance section as an agent judgment and explicitly not Weibao's own
signature, in the same shape `16A-REVIEW.md` used. It was not a rubber stamp: it
raised seven findings, all carried into the freeze record's open items with
owners, and it flagged one backstop marker (16B-09's long-running-job claim) for
a later human pass rather than accepting it silently. Its strongest finding is
that `Needs reconciliation` is written in operation-protocol vocabulary rather
than a learner's.

## Freeze-gate fixtures

Four of five `passed`. `APP-02` is `weaker proof`: the two layouts are
distinguished only by a viewport-hint header, so what is proven is one route and
one identical back href serving both widths, not rendered layout at either
width, which is Phase 17A's; and the browser half of the focus-restoration
scenario is not observed by any check here. Both limits are stated in the tracer
report and in the freeze record rather than glossed.

## Deviations from this plan, with reasons

**1. The plan said no change is made to any shipped file, and one was.** Its
"Artifacts this phase produces" section says that if the review finds a defect,
the fix is a new plan and not a task here. The change made was to
`tests/retention_roundtrip.py`, and it was not a review finding: it was a
failing freeze leg, put to Weibao as a decision, and made on his instruction. No
production file changed in this plan.

**2. `python3` for `python`, and the suite run with
`ANKI_CONNECT_URL=http://127.0.0.1:1/`.** Carried forward from
`16B-02-SUMMARY.md` and stated in the tracer report.

## Artifacts created

- `16B-TRACER-REPORT.md`: what was run, the five-fixture table, measured
  figures with the machine and Python version named, additivity evidence, and
  open findings including all 25 backstop markers.
- `16B-REVIEW.md`: verdict, provenance, answers to all ten question groups, a
  per-item judgment on the backstop list, and seven findings.
- `16B-FREEZE.md`: opens with `## Frozen at 16B`, enumerates the published
  surface, states what is not frozen with Phases 14B, 16A, 16C, and 17A named
  as owners plus the six UI-SPEC deferral rows verbatim, records the evidence,
  and lists open items with owners.
- `16B-DECISIONS.md`: `## D-16B-13. Freeze scope` appended.
- `16B-VALIDATION.md`: status `validated`, `nyquist_compliant: true`,
  `wave_0_complete: true`, every Status cell resolved, the measured runtime
  recorded, and every sign-off box resolved with the review-leg caveat stated
  rather than hidden.
