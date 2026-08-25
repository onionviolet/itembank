# Prompt: finish the work the 13.9 sitting opened

Written 2026-08-24 after Weibao sat the rebuilt EMT bank end to end. The
sitting completed (ten items, nine auto-scored, one short marked `fail`), and
it produced a queue of real defects and decisions that outlived it. This prompt
is that queue, ordered, with the reasoning that produced the order.

Read `.planning/EXEC-CONTEXT.md` first. Do NOT read `ROADMAP.md`,
`REQUIREMENTS.md`, `UI-SPEC.md`, `AGENT-WORKFLOW.md` or `SOURCE-TO-COURSE.md`;
that stack is about 122,000 tokens and every task below cites what it needs.

## Ground truth you can rely on

- Full suite was green at the time of writing, `itembank guard .` clean.
- The sitting: session `13d56ab15efb4709821a6dd86357a5dc`, course root
  `~/Documents/itembank-courses/emt-unit-1`, status `complete`, 18 auto
  attempts, 9 auto correct, 1 human mark (`q8`, `fail`), 10 objectives touched.
- `_evidence/evidence.jsonl` in that course root holds 33 lines for 1 real
  response, 1 mark, and a set of `session_start` probe events that are all
  retracted. `evidence --objective` returns honest numbers; the raw line count
  does not. Any calibration write must state this.
- Standards research with verified citations and verified NEGATIVE findings:
  `.planning/research/2026-08-24-item-writing-standards.md`. Read it before
  citing any standard. Several obvious-sounding authorities say nothing about
  item writing, and that file records which.

## Rules you cannot break

1. The runtime owns correctness, session state, evidence, and keyed assessment
   disclosure. No model settles a score or decides key disclosure.
2. One parser (`model.py`), one scorer (`runtime.py`), one evidence store, one
   writer (`journal.commit_operation`).
3. Evidence and banks stay on disk. No telemetry.
4. Format changes are additive.
5. No em dash characters anywhere, commit messages included.
6. `python3`, not `python`. Standard library only for runtime code.
7. `ANKI_CONNECT_URL=http://127.0.0.1:59999` when running the suite, or quit
   Anki. Two suites assert the Anki-unavailable path and Anki is running on
   this Mac.

## The queue

### 1. The attempt markdown is never written on the browser path

**Blocks 13.9-03.** Its Task 1 verify says "An attempt record exists under
`<course-root>/_attempts/`". It does not, and never has for a `serve` sitting:
`_refresh_attempt_view` is called only from the JSON `/api/submit` path
(`surfaces/daemon.py:1545`, `:2831`); the browser form branch returns at
`daemon.py:1483` without it. The route's own docstring at `daemon.py:1428`
claims the opposite, so one of the two is wrong and the code is what shipped.

The typed prose is safe in `evidence.jsonl`, so this is a missing second copy,
not data loss. Decide deliberately whether the attempt file is still a product
surface or a superseded one, and make the docstring and the code agree either
way. If it stays, the form path must refresh it; if it goes, 13.9-03's verify
step needs rewording and the `serve` banner must stop printing a path it never
writes.

### 2. A failed submit still discards the learner's typed answer

The `403` that ate Weibao's prose is fixed at its trigger (`QUIZ_TOKEN_TTL` is
now four hours, `13e3446`), but not as a class. A network blip, a server
restart or a stray reload does the same thing. Findings, all verified:

- No draft persistence anywhere. Zero hits for `localStorage`,
  `sessionStorage` or autosave. The textarea at `quiz_page.py:543` has no id
  and no value.
- The graded sitting is a plain non-JS form POST: `start()` returns early at
  `quiz_page.py:3214` on the server baseline, before installing any submit
  handler, so the browser does a full navigation and the page is gone.
- The 403 renders a bare error document (`daemon.py:1466` into `send_error`)
  with no link, no retry and no echo of what was written.
- The token is popped at `daemon.py:1461` BEFORE `do_action` runs at `:1473`,
  so any later failure burns it and Back-then-resubmit 403s too.

Order that matters: echo the submitted answer back into the textarea on every
non-success path first (small, needs no client JS, fits the script-free
baseline), then stop spending the token until the action succeeds, then
consider draft autosave, which is the only one of the three that survives a
server restart. Draft state is presentation state and must never become a
second source of truth.

### 3. Multi-select feedback that rules out wrong answers

Weibao's own words, recorded verbatim in `USER-VISION.md` under 2026-08-24:
"its just to rule out wrong answers and also show what I got right so I can
keep on going rather than gambling". **He is explicit this is NOT partial
credit.** Do not change the scorer.

The authored per-option rationale already exists (`DA:` for all eight letters)
and already flows through `explain_payload`. What is missing is the disclosure
policy deciding when the runtime releases it. Add it to `FEEDBACK_POLICIES` and
`teaching_transition`:

- first not-fully-correct attempt: name which of the learner's OWN selections
  were right and which were wrong, without touching options they did not pick;
- after the item settles: the full per-option DA;
- exam and diagnostic stay silent, which preserves fidelity to how the real
  examination behaves.

NREMT scores dichotomously and gives no credit for a partially correct
response, so the existing all-or-nothing `multi` scoring is already conformant
for EMT and must not become partial credit. See the research file.

### 4. NREMT structural conformance, as a subject-scoped lint rule

`q8`'s bank has one divergence: `q3` is 2 correct of 6 options. NREMT permits
2-of-5 or 3-of-6 with exactly three incorrect, and `mc` is 1-of-4. Both are
mechanically checkable and belong in `model.lint`.

**The rule must be subject-scoped.** NREMT binds EMT and has no authority over
Math 1400 or CSCI 1100; a linter demanding four options everywhere would be
wrong on two of the three subjects. `subjects.py` already exists for this.

Tier the wider item-craft work the same way the research file does: tier 1
mechanical checks as errors, tier 2 heuristics as suppressible warnings, tier 3
semantic judgements NOT as lint rules at all but as an advisory model-assisted
review a human accepts. A lint rule with a high false-positive rate is worse
than no rule.

### 5. Empirical distractor analysis

The strongest available item-quality signal, needing no model and no external
authority: flag any distractor chosen by zero learners across N attempts. The
evidence store already holds what this needs. It gets better with every
sitting and it is the one check no standards body can give.

### 6. Then, and only then, 13.9-03 Tasks 2 and 3

Write `13.9-CALIBRATION.md` from the real sitting: pointers, counts and hashes
only, never item text, and both denominators stated. Then A9 closure and the
STATE roll-up. The 13.5 waiver checkbox is already closed (`4d4c90d`); four A9
boxes remain.

Do this LAST. Items 1 and 2 change what a sitting produces and how it is
recorded, and a calibration file written before them would describe a surface
that is about to change.

## Known-open, deliberately not queued

- `Item 1 of 0`, and the position never advancing. Owned by 13.5 defect D2,
  which already has an unexecuted plan at
  `.planning/quick/260817-q7d-fix-135-defects-d1-d2/`. Do not fix it here; run
  that plan.
- The serve banner prints a `session` id that is NOT the id evidence is written
  under. Recorded in `13.9-DECISIONS.md` 2026-08-24. Cosmetic until someone
  trusts the banner; the corrected instruction is already recorded beside it.
- A second submit in exam mode returns `hold` rather than a deferred action.
  Observed on a fixture, not chased, not understood.
- `explain_payload(q, reveal=False)` blanks `model` and `rubric` and returns
  the same text in `answer_text`. It does NOT reach the wire on the served
  short path, verified; the only variable-`reveal` caller is the offline static
  build. A landmine rather than a live leak, worth closing as defence in depth.
- Marking ergonomics for a solo learner-marker: no `--notes` flag, `--rubric`
  requires retyping each point's full text, and nothing lists what is awaiting
  a mark across sessions.

## How to work

Commit after every task with a pathspec, conventional prefix, and what was
wrong rather than what you touched. Never `git add .`. Do not push. Run the
suites your change touches plus `python3 itembank.py guard .`.

**Two cautions earned the hard way on 2026-08-24.** A suite of 70 green tests
agreed with a broken served page all night; when the change is user-facing,
drive the real page before believing the suite. And a test can pin a defect:
`agent_roundtrip` asserted `pending_manual >= 1` after a mark, which encoded
the exact bug it was later used to catch. When a test fails after a fix, decide
which of the two is wrong before editing either.
