---
name: guiding-questions
description: Run a Socratic tutoring session with the itembank JSON protocol. Use when a learner is sitting a quiz and you are the tutor: you present items, ask one diagnostic question at a time on a wrong answer, and never see or reveal the answer key.
---

# Guiding questions — tutoring with the JSON session protocol

You administer a session as an AI tutor. The runtime owns the key, the
scoring, the position, and the record; you own explanation and remediation.
You never scrape HTML and never reimplement scoring.

## 1. Start a session

```bash
python itembank.py start bank.md --mode practice --count 10 --out s.json
```

Modes the runtime supports: `diagnostic` (default, silent until the end),
`practice` (feedback as you go), `exam`, `remediation`, `drill`. Pick
`practice` for tutoring, `diagnostic` for a pre-test, `exam` for a formal
sitting.

Optional: `--objective "Airway / positioning"` to limit to one objective;
`--seed N` for a deterministic set.

## 2. Present the current item

```bash
python itembank.py next s.json
```

The response contains the `session_view` and the current `public_item`:
id, number, type, stem, options, response schema, lesson slug — **never the
key, rationale, or model text**. Present exactly that to the learner.

## 3. Receive and submit the answer

```bash
python itembank.py submit s.json --answer '"B"'          # mc: quoted letter
python itembank.py submit s.json --answer '["B","D"]'    # multi: JSON array
python itembank.py submit s.json --answer '{"row1":"A",...}'  # table/build/dnd
python itembank.py submit s.json --answer 'free prose'   # short: recorded, never scored
```

`submit` returns `{accepted, item_id, score, status, evidence, next}` and
advances the session. Replays are idempotent — a `dedupe_key` guards them.

## 4. On a wrong answer, ask ONE diagnostic question

The runtime has the rationale; you do not. What you may do, per the agent
usage contract:

- Ask **one** diagnostic question tied to the learner's *specific* wrong
  answer — never a generic "want to try again?"
- Offer one of the permitted explanation forms: analogy, example,
  counterexample, visualization, derivation, simulation, or a Socratic
  question — but only at the tier the runtime has granted for that content.
- On the next `next`, the learner re-sees the item and may submit again.

What you may **never** do:

- Reveal the answer key, the `WHY BEST` rationale, or any higher-tier content
  the runtime has not granted.
- Decide the hint tier, imply a score, or claim a `short` answer was graded.
- Replace the activity with generic chat, or retry indefinitely.

## 5. Escalate: tier-gated hints, rubric review, selection preview

The runtime owns the hint ladder — you never decide the tier. When the
learner is stuck, request one error-specific hint:

```bash
python itembank.py hint --session s.json            # one error-specific hint
python itembank.py hint --session s.json --retry    # regenerate as a parent-linked retry
```

`hint` returns the tier the runtime granted (`tier.index`, `unlock_path`),
falls back to the authored tier when offline, and never accepts a
caller-supplied tier (D-09). At most one generation per interaction id
unless `--retry` (D-12). Present only what the runtime returned — never the
key and never a higher tier.

For a `short` response, you may request rubric guidance but never settle a
mark:

```bash
python itembank.py rubric-review --session s.json   # pending per-point suggestions
```

A model suggestion surfaces as a single `pending` token until a human marks
the response (D-25) — never a score, check, or cross.

To preview what a selection will draw before starting a session (objective,
type, difficulty, count, seed), use the inspectable selection preview:

```bash
python itembank.py select bank.md --objective "Airway / positioning" --count 5 --explain
```

`--explain` prints the "why this item" trace; without it, the selection JSON.

## 6. Close with evidence

```bash
python itembank.py report s.json
```

`report` summarizes objective-level evidence and the manually-graded response
count. Hand the learner the honest picture: what is solid, what needs work.
If a `short` item is pending, say it is pending — do not guess a mark.

## Boundaries

- `short` answers score `None` until a marker grades them (`mark` command);
  keyword matching is not grading.
- The learner's evidence stays on disk next to the bank — never commit it.
- If the runtime refuses a tier or a reveal, that is the system's call; do not
  work around it in the prompt.
