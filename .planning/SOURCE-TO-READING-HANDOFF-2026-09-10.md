# Source-to-reading chain handoff

Date: 2026-09-10
Status: Link P1 implemented and deterministically verified. Weibao accepted the
rebuilt visual direction as fitting enough to continue on 2026-09-10. Future
refinement and human accessibility checks remain open.

GOAL: Review the reversible reading-occurrence prototype, then decide whether
to authorize Link P2's additive course-graph and evidence contract design.

OWNER: Weibao owns LA-Q1, the Sources versus Resources learner label, and
LA-Q2, the permanent occurrence-to-binding reference. The implementation owner
owns technical fit and verification.

SCOPE: Review `prototypes/course-preparation/` and the P1 gate. If both product
choices are accepted, specify the smallest durable delta described in
`SOURCE-TO-READING-IMPLEMENTATION-PLAN-2026-09-10.md` P2. Use one writer for the
course graph and evidence contract because their identities must agree.

DO NOT TOUCH: real course data, production imports, scoring authority, external
services, the existing dirty vision-audit files, commits, or pushes. Do not
infer legacy activity metadata or completion. Do not begin P3 recovery work in
the same writer lane.

CONTEXT: The prototype creates a disposable synthetic course through real
course, journal, rights, objective, source, and direct-reading binding
operations. It projects three in-memory occurrences. Two are Now activities and
one stays in Library. Browser Mark read state resets on reload and is visibly
labeled simulated.

EVIDENCE:

- Added `.planning/SOURCE-TO-READING-IMPLEMENTATION-PLAN-2026-09-10.md`.
- Added `prototypes/course-preparation/README.md`, `source.md`, and
  `build_prototype.py`.
- Added `tests/course_preparation_prototype_roundtrip.py`.
- `python3 tests/course_preparation_prototype_roundtrip.py` passed.
- `python3 scripts/preflight.py --quick` passed every executed gate. Full
  Python, clean-tree, and JavaScript gates were skipped by quick mode.
- `git diff --check` passed.
- Generated review output is `/tmp/itembank-course-preparation/index.html`.
  It was opened in the Codex file viewer. No browser screenshots were captured.
- Existing unrelated dirty and untracked files were preserved.

AUDITS: `.planning/SOURCE-TO-READING-COMBINED-AUDIT-2026-09-08.md` remains the
semantic owner. `.planning/SOURCE-TO-READING-NEXT-PACKET-2026-09-08.md` owns R1
through R3. P1 reconciles neither recovery finding because imports are outside
its scope.

NEXT ACTION: Decide LA-Q1 and LA-Q2. If accepted, invoke `$daisy-chain-work` and `$efficient-agent-routing`
for Link P2 using this packet. Start by locating the course graph parser and
canonical event schema, then draft the additive contract before production
code.

GATE: P2 may start only with explicit product acceptance of the learner label
and permanent binding reference. P2 completes only when compatibility,
idempotency, shared-content isolation, rights/revision states, and export or
restore loss reporting are specified and independently reviewed. Human touch,
screen-reader, 200 percent text, 400 percent zoom, and aesthetic checks remain
owed until performed.

RETURN: Decisions for LA-Q1 and LA-Q2, exact contract delta, files changed,
targeted checks, independent review findings, migration impact, recovery path,
and every still-owed human or P3 gate.
