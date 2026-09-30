# Next question workflow packet

Execution status: R1/A2 source and package journeys are recorded in the
[dated audit section](WORKFLOW-AUDIT-2026-09-29.md#a2-implementation-evidence-2026-09-29).
This packet preserves the original handoff. The next unit is
[the A3 ordering packet](NEXT-ORDERING-PACKET-2026-09-29.md). Live pointer drag,
human accessibility and installed acceptance remain open.

Dispatched successor: `01a0efcd-8f8d-7d72-ba79-5d0d1fa33f9d`, local project
chat titled "Repair exam disclosure and complete matching workflows".
An initial wait snapshot confirmed its turn is active. The predecessor has
finished source writes and relinquished its repair paths to this packet.

GOAL: Repair cross-surface exam disclosure, then implement an explicit bounded
one-to-one matching workflow through authoring, ordinary served response,
runtime checking, feedback, restart and recovery. Keep ordering/Parsons as A3,
with a concrete contract and follow-up scope rather than silently dropping it.

OWNER: User decides product direction; runtime owns scoring, session state and
keyed disclosure. This new chat owns the named successor unit after checking
live shared-file ownership and fingerprints.

BASE: Shared local project checkout, commit
`8ccd45832b66b0b86bb406d6232ef0633ef71dc3`, with substantial unrelated dirty work.
The following SHA-256 values identify relevant inputs at handoff:

| Input | SHA-256 |
| --- | --- |
| surfaces/quiz_page.py | 8e695bce9d4118e85c9fa759b2a421c5f5f2856929d1d02c64529bf1a2182c5f |
| tests/js/question_workflow_recovery.test.mjs | 765a3a34249169d0a451d3aacb5e3504729a33d3ab0c21f91018bc5cae583003 |
| tests/question_workflow_recovery_roundtrip.py | ac63610c392d298b2b3b6a25d4039d297dd5da418c57442b71946f2f63bab273 |
| surfaces/home.py | 79b11fdd611761a4b28cfb8551d6ec006e41aea185061ecb7302c3bf0584e527 |
| runtime.py | 9651d3139a43578575a519e908d1855aa57439bf0e6fe3a685b90e256bea93a3 |
| surfaces/daemon.py | 38a12a1bb6bea5f4bd81e580ae417bbeeaefd5615aa54a80af699c850274bcd9 |

AUTHORITY: User requested repairs and a new chat. Scoped code, synthetic tests,
contract design and evidence updates are authorized. No commit, push, merge,
installation, release, donor-library copying, external service or learner-file
mutation is authorized by this packet. Read applicable instructions and current
owners first. Contract changes remain additive and reviewed against the binding
product rules. Do not treat this packet as a new scoring authority.

SCOPE: First trace `surfaces/home.py:_activity()` and the corresponding Activity/
report routes to runtime disclosure policy. Implement one shared authorized
projection instead of inventing separate mode checks per surface. Owning files
may include runtime, Home, evidence/report adapters and narrowly scoped daemon
routes. Then define stable choice/row identity and explicit matching capacity
using the smallest compatible parser/schema/runtime extension, native and rich
quiz controls, authoring validation and the existing proposal/journal path.
Use source windows and named tests; avoid whole-file reads of large modules.

DO NOT TOUCH: Concurrent theme, Home/Courses layout, instruction/skill repairs,
private course files, collected coursework, installed learner sessions and
unrelated dirty paths. Preserve inherited quiz changes and this A1 repair.
Check current owners before touching a shared module; reconcile changes rather
than reverting or staging the entire tree. No external communication beyond
the user-authorized new chat is needed.

CONTEXT: The [workflow audit](WORKFLOW-AUDIT-2026-09-29.md) covers all F1-F10
families and pins upstream source patterns. W1/W2 are repaired; W3/W4 semantics
and W5 complete-family acceptance remain open. The authoring/journal foundation
already exists. One-to-one keyed mappings can already be compared; explicit
capacity/construction/validity and authoring are the missing contract. Do not
build a second scorer. Learn from H5P state/keyboard lifecycle, PrairieLearn
prepare/render/parse/grade separation and dependency contracts, Runestone
workspace recovery, and STACK authored answer/misconception test cases.

EVIDENCE: Source and packaged `tests/question_workflow_recovery_roundtrip.py`
pass two normal form submissions, refused retries and quiz exam withholding.
The packaged browser preserved assignment and partial build drafts through
reload and a desk/back detour, and recorded both responses exactly once.
All 88 JavaScript tests, inline HTML, scoring, serve and quick preflight passed.
The disposable package SHA-256 is
`ab4189d2450003f58b5358dcb53588ccf1c819b6a49e7637894d9097eba1458a`;
its quiz module matches the fingerprint above. Proofs and task-isolated repair
patch are ignored under `dist/a1-recovery-20260929/`. The latest repair did not
repeat full preflight; prior full-suite theme/dirty-tree failures remain named.
Human accessibility and native-shell installation are not accepted.

NEXT ACTION: Use the existing synthetic `--browser-hold` fixture under a PTY.
In exam mode submit only the first item, then open the desk while the second
item is unanswered. Observe `Answered q1 (correct)`. Trace `_activity()` raw
score formatting and test disclosure across Home/Activity/report. Repair this
before adding matching semantics. The fixture is disposable and cleans up on
Enter; do not reuse the real installed app.

GATE: An unfinished formal sitting exposes no withheld item verdict or rationale
in the quiz, Home, Activity or report surfaces; released feedback still works
under runtime policy. Raw evidence remains accurate. Then author and preview
two matching tasks with duplicate labels, stable identities, explicit reuse
rules and distractors where supported. Complete, revise, reject invalid reuse,
resume, refuse/retry, score and report through the same runtime and normal
served path. Keep old dnd semantics and old evidence compatible. Validate a
fresh packaged candidate and run the appropriate owning gates. Run one final
full preflight only on the integrated candidate, explaining any inherited
failure rather than clearing unrelated work. Human-only checks stay named.

RETURN: Actual changed paths, fingerprinted source/package evidence, resolved
findings, remaining limitations and the concrete A3 ordering packet. Update
the existing backlog/audit and STATE projection without creating another queue.
Do not declare the whole F1 family complete from one widget or isolated fixture.
