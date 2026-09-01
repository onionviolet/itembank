# Cold-agent onboarding transcript (A10 check 2's fixture)

**Recorded:** 2026-09-01 · **Mechanics:** 18-CONTEXT D-04, executed by
18-03 Task 3 · **Runs:** two, both kept. Run 1 completed the walkthrough
and surfaced defects; the defects were fixed in README.md and run 2, a
second cold agent against the fixed copy, completed cleanly. A failed or
confused run is never shrugged off: every confusion below either became a
README fix (listed under Defects fixed) or a named defect routed onward
(listed under Named defects routed onward).

## Redaction rules (stated per the plan, applied to both transcripts)

- Real absolute filesystem paths are replaced with placeholders: the
  repository checkout is `USER-DIR/itembank`, the agent's scratch
  directory is `SCRATCH-DIR`.
- No real personal names, subjects, emails, or machine names appear. The
  simulated user's study material is synthetic (invented astronomy facts
  in run 1, invented geology facts in run 2) and stays synthetic; no real
  learner content enters this repository. `itembank guard` is the
  backstop and exits 0 on this tree.
- Agent and model identifiers may remain: both runs were Claude
  general-purpose subagents spawned cold from this executor session.
- The narrations are otherwise verbatim, including their em dash
  characters, under the repository prose rule's verbatim-quotation
  exception; the framing text of this file uses none.

## Cold-start conditions

Each agent was told only: the repository location, that it must use
nothing but README.md and capabilities.json (AGENTS.md, `.planning/`, and
`.claude/` explicitly forbidden), to walk a simulated new user through the
README's AI-assistant checklist with synthetic material, to write only in
its own scratch directory, and to narrate every command and every
confusion. Neither prompt contained any project knowledge. Both runs
executed on a macOS host where `python` is absent and `python3` is 3.14.6;
the actual download was skipped (the checkout stood in for the fetch), so
the Gatekeeper and SmartScreen steps were read but not exercised; they
remain owed to the second-person cold install (18-GATES.md row 7).

## Defects fixed between run 1 and run 2 (all README.md copy)

1. The "whole format" sample did not parse at all: markers were indented,
   options shared one line, and `[TYPE: short]` sat inline in the stem,
   while the parser requires each structural marker at the start of its
   own line. Found by this executor's own fresh-install pass minutes
   before run 1 started (run 1 read the already-fixed sample and
   confirmed it). Fixed: the sample is now a lint-clean file and the
   surrounding copy states the left-margin rule.
2. `python` versus `python3`: every command block said `python`, which
   fails verbatim on macOS. Fixed: Path 2 now uses `python3` and a
   quick-start note covers the substitution for the whole README.
3. The first-launch update-notice sentence implied any first launch
   prints it; only the first daemon launch on a machine that has never
   seen it does, and bank commands never check. Fixed in the Install
   section.
4. "Lints clean" ambiguity: a structurally valid first bank emits many
   advisory warnings, which run 1 found disorienting. Fixed: the format
   section now says errors block, warnings advise, and names the three
   expected first-run warnings.
5. The agent-driver section never mentioned `response_schema` (the
   authoritative answer-shape contract) or the short-item end-of-sitting
   signal. Fixed: a contract-details list was added.

## Defects fixed after run 2 (README.md copy, no third run required since
run 2 completed cleanly and these close its remaining confusions)

6. Practice-mode `action: "hold"` (a wrong answer does not advance the
   session; `next` re-serves the same item) was undocumented and cost run
   2 a two-minute driver loop. Added to the contract-details list.
7. The item after a successful `submit` arrives nested under the `next`
   key; now stated in the same list.
8. Skill-count mismatch ("five playbooks" versus the ten directories
   capabilities.json lists) and a stale "seven types" in the Layout
   section against "Eight types ship"; both corrected.

## Named defects routed onward (bigger than README copy, out of this
plan's file list; recorded, not patched here)

- N-01: `itembank spec` numbers the eight item types 1 to 6, then 8,
  then 7 (both runs tripped on it). Owner: the model layer's spec text.
- N-02: `submit` accepts a wrong-shaped answer against the current item
  (`accepted: true, score: false`) instead of rejecting it as malformed,
  consuming an attempt; run 1 recorded a wrong attempt this way. Owner:
  the runtime's submit validation.
- N-03: `start`'s selection `trace` block is verbose enough that run 2
  called wading to `item` a burden for an agent driver. Owner: session
  protocol ergonomics.

## Run 1 transcript (2026-09-01, completed; verbatim, redacted)

The README modification is not mine: the diff is an authorial edit to the README's own sample (mtime 01:33, made by some concurrent process outside this session; I ran no write into the repo, and the flow I read was already the edited version). I left it alone. Server is down, no processes remain. Onboarding is complete; here is the full narration.

---

# Cold-start onboarding walkthrough (README + capabilities.json only)

**What the tool is:** itembank is a local-first assessment runtime: you author exam-style question banks in plain markdown, a linter enforces the format contract (plus two quality rules: distractors must say when they would be correct, and answer positions must not skew), and one deterministic scorer grades every sitting. Sittings run either in a browser via a loopback server (`serve`, key never sent to the browser) or through a key-free JSON session protocol for AI tutors. All evidence stays on disk. A larger "source-to-course" workspace is described but explicitly not shipped.

## Step-by-step

**Step 0 — capabilities.json.** Read it first as instructed. Version 0.3.0, format contract 1, 50 commands, ~45 served routes, 10 skills. `changed_for_agents` has one entry (capabilities.json's own introduction).

**Step 1 — Verify Python.**
- Ran: `python3 --version` and `python --version`
- Printed: `Python 3.14.6` / `command not found: python`
- 3.14.6 ≥ 3.11, requirement met. Note: the README's own Path-2 quick start says `python itembank.py --help`, which fails verbatim on this macOS machine; only step 1 of the AI checklist acknowledges `python3`.

**Step 2 — Fetch the code.** Skipped the actual clone per my instructions; treated the existing checkout at `USER-DIR/itembank` as the fetched code.

**Step 3 — Verify the runtime.**
- Ran: `python3 itembank.py --help` → printed the full command index matching capabilities.json.
- Ran: `python3 itembank.py spec` → 454-line format contract. Read in full before authoring.
- The README/Install section says the first launch prints a one-time update-check notice; nothing of the sort appeared (possibly because this checkout has already run, but a truly new user can't tell).

**Step 4 — Author and lint the first bank.** Wrote 7 synthetic astronomy items (3 mc, 1 multi, 1 table, 1 build, 1 short) to `SCRATCH-DIR/cold-agent-run/astronomy_basics.md`.
- First lint: `0 errors, 17 warnings, exit=0` — warnings: no `[ID:]`, objectives lacking a `subject:` prefix, and missing `SECOND-BEST` on mc items. None of these three requirements are visible in the README sample or prominent in `spec` (the sample in the README lints clean but warns in practice, presumably — the README claims "This sample lints clean as written", which is true only if "clean" means zero errors, not zero warnings).
- Fixed all three (prefixes → `astro:*`, added SECOND-BEST lines, ran `id-assign` which minted ids and sha256 fingerprints into the file).
- Final lint: **`7 items, 0 errors, 0 warnings`**.

**Step 5 — First graded sitting.**
- Ran: `python3 itembank.py serve astronomy_basics.md --no-open` (background). It printed the session id, the attempt path (`_attempts/astronomy_basics_attempt_2026-09-01_0136.md` beside the bank), and `http://127.0.0.1:8731/quiz/astronomy_basics`.
- `curl` on the URL → HTTP 200. Verified the README's key claim: the page HTML contains zero item content (no "Jupiter", no rationale text); items arrive per-request from the process, and every "correct" string in the page is UI copy like "Not correct."
- Then sat a full graded session through the documented agent path: `start --count 7 --mode practice --out s.json`, then `next`/`submit` per item, then `report`. Result: **6/7 auto-correct, 1 short answer recorded `pending`** for a human marker, per-objective breakdown and teaching outcomes in the report. Evidence landed in `_attempts/session_*.json` and `_evidence/evidence.jsonl` beside the bank in my scratch dir, exactly as promised.
- Shut down: killed the serve process; `curl` now fails and `pgrep` finds no itembank process. **Nothing left running.**

**Steps 6–9 (relayed, not exercised):** `study`, `lesson`, `day`, `export` exist for the rest of the loop; the course workspace is direction, not shipped; evidence stays on disk; never commit real banks (`guard` enforces this).

**Repo integrity:** I created/modified nothing inside the repository. `git status` does show `README.md` modified plus two untracked files, but the diff is an authorial README edit (expanding its own format sample) with an mtime during my session, made by a concurrent process that is not me; I read the already-edited version and left it untouched.

## Points of confusion

1. **`python` vs `python3`.** The README's Path-2 quick start and all Use-section examples say `python itembank.py ...`; on this macOS machine `python` does not exist. Only checklist step 1 hints at `python3`, and it frames `python` as the Windows spelling. Every command block would fail if pasted verbatim.
2. **The promised first-launch update-check notice never appeared.** Install section: "The first launch prints this notice once before it checks anything." Nothing was printed across any invocation, and a newcomer cannot tell whether the check happened silently, was already consumed, or is daemon-only.
3. **"Lints clean" is ambiguous.** The README says its sample "lints clean as written," but a structurally valid bank still emits many warnings (missing `[ID:]`, un-prefixed objectives, missing `SECOND-BEST`). None of those three expectations appear in the README sample, and `SECOND-BEST`/the `subject:path` objective convention are easy to miss even in `spec` (the objective-prefix rule is not in `spec` at all as far as I saw; it surfaces only as a lint warning).
4. **Spec numbering is out of order:** the eight item types are numbered 1–6, then 8 (check), then 7 (visual). Harmless but disorienting when checking you read all of them.
5. **`submit` applies to whatever is current and accepts wrong-shaped answers.** Submitting a table-shaped dict against an mc item was `accepted: true, score: false` rather than rejected as malformed, and it consumed an attempt. An agent that loses track of the cursor silently records a wrong attempt. (The teaching-outcome record for q3 now honestly says `correct_after_attempts: 2`, which is my slip immortalized as learner evidence.)
6. **A session ending on a `short` item never reaches `complete` via `submit`.** The final short answer returns `action: defer_feedback` forever and the session stays `active`; the README's agent loop ("submit ... returns the next item") gives no termination signal, so my driver looped until its own bound. `report` showing `pending_manual: 1` is the real end-state signal, but that has to be inferred.
7. **`build`'s public payload shape differs from `table`'s:** table rows are `{text, id}` objects answered by id; build steps are bare strings answered by text. Both are discoverable from `response_schema`, but I guessed wrong first (my driver assumed step objects) — the README never mentions `response_schema`, which turned out to be the most important field for an agent.
8. **README samples in flux:** the README's format sample was edited on disk mid-session by some other process; the git snapshot said clean at start. Not a documentation defect, but a cold agent verifying "repo untouched" will trip on it.
9. **Minor:** `serve` chose port 8731 as documented, and `id-assign` is correctly flagged as the only bank-writing command; but nothing in the README warns that `lint`'s 17 warnings are the expected first-run experience, which could make a newcomer think they misread the spec.

**Verdict:** Yes — a newcomer agent can complete onboarding from the README alone (the checklist is unusually good and every claim I tested held), provided it substitutes `python3` on its own and treats `response_schema` in the JSON payloads as the authoritative answer-shape contract.

## Run 2 transcript (2026-09-01, after the fixes; completed cleanly;
verbatim, redacted)

Onboarding complete. Here is the full narrated walkthrough, which is the deliverable.

## What the tool is

itembank (v0.3.0 per capabilities.json) is a local-first, Python-stdlib-only assessment runtime: you author exam-style question banks in a small markdown format, `lint` validates them with per-item errors, and one runtime scores every surface — a browser sitting (`serve`), an offline HTML file (`build`), and a key-free JSON session protocol for AI tutors (`start`/`next`/`submit`/`report`). Evidence stays on disk; the answer key never reaches the client before the learner answers. capabilities.json is the machine-readable index: 53 CLI commands, ~45 served routes, a skill list, and a `changed_for_agents` changelog (one entry, 0.3.0, introducing the file itself).

## Step-by-step narration (README's AI-assistant checklist)

**Step 0 — read capabilities.json.** Read `USER-DIR/itembank/capabilities.json`. Version 0.3.0, format contract version 1, every command since 0.3.0. Matched what `--help` later printed. No surprises, except that the README calls the repo skills "five playbooks" while capabilities.json lists ten (three are stubs; the skills tree confirms this labeling elsewhere, but from README + capabilities.json alone the counts disagree).

**Step 1 — verify Python.** `python3 --version` → `Python 3.14.6`. Passes the 3.11+ requirement. The README's interpreter note (`python3` on macOS) was accurate.

**Step 2 — fetch the code.** Skipped: the checkout at `USER-DIR/itembank` was treated as already fetched. No Gatekeeper/SmartScreen handling needed.

**Step 3 — verify the runtime.** `python3 itembank.py --help` printed the full command index (exit 0). `python3 itembank.py spec` printed a 454-line format contract. Reading it was essential: the README's format sample alone would not have taught me DISTRACTOR ANALYSIS bullets, RUBRIC minimums, or the table/build/dnd line grammars.

**Step 4 — author a first bank, lint until clean.** Wrote synthetic geology material (rock classes, Mohs scale, Earth's layers, plate boundaries) as 7 items (3 mc, 1 multi, 1 table, 1 build, 1 short) at
`SCRATCH-DIR/cold-agent-run-2/geology_bank.md`.

- `itembank lint geology_bank.md` → `7 items, 0 errors, 7 warnings`, exit 0. Every warning was the predicted `no [ID:] line; run itembank id-assign`. The README's other predicted first-run warnings (missing SECOND-BEST, unprefixed objectives) did not appear because the spec had already taught me to include them — evidence the "read spec before authoring" ordering works.
- `itembank id-assign geology_bank.md` → 7 ids and 7 content hashes minted, written into the bank (the one command allowed to write into a bank).
- Re-lint → **`7 items, 0 errors, 0 warnings`**, fully clean on the second pass.

**Step 5a — graded sitting via the JSON session protocol.**
- `itembank start geology_bank.md --count 7 --mode practice --out s.json` → session created, items shuffled (q5 first), first item delivered with `response_schema` and no key, plus a very verbose `trace` block justifying each selection.
- Submitted the table item `{"0":"Igneous","1":"Sedimentary","2":"Metamorphic","3":"Sedimentary"}` → `score: true`, evidence event recorded. Note: the next item arrives nested under `next`, not at the top level.
- **I then hit a real snag.** I deliberately answered q2 wrong ("D") to exercise the report. My driver loop assumed submit always advances; it timed out after 2 minutes. Diagnosis: in practice mode a wrong answer returns `{"accepted": false, "score": false, "action": "hold"}` and `next` keeps returning the same item — retry-until-correct. My loop re-submitted the identical wrong answer forever (harmlessly: the evidence log deduped it to one event). Neither the README's four-line agent-driver recipe nor its "two contract details an agent driver needs" paragraph mentions the `action: hold` / non-advancing behavior.
- After handling `hold`, the rest went cleanly: q2 "C" → correct; q1 "A", q6 ordered step texts, q4 `["A","C","D"]` all `score: true`; the schemas (`build` answers by step text array, `multi` by letter array) matched the README's `response_schema`-is-authoritative claim.
- The final `short` item returned `score: null, action: "defer_feedback", status: "active"` — exactly the README's warning that there is no complete signal and `report`'s pending count is the end-of-sitting signal.
- `itembank report s.json` → `auto_attempts: 7, auto_correct: 6, pending_manual: 1`, per-objective breakdown, and per-item teaching outcomes correctly showing q2 as `correct_after_attempts: 2` and q7 as `pending`.

**Step 5b — serve flow.** `itembank serve geology_bank.md --no-open` (background) printed the session id, the attempt-file path (written beside the bank in `_attempts/`), and `url http://127.0.0.1:8731/quiz/geology_bank`. `curl` → HTTP 200, 131,858 bytes, and `grep -c "CORRECT:"` on the page → 0: the served page really does not contain the key. Killed the process; confirmed the port no longer answers and `pgrep` finds no itembank processes. Nothing left running.

**Steps 6-9 (relayed, not executed):** `study`/`lesson`/`day`/`export` for the rest of the loop; `update` for freshness; the course workspace is direction, not shipped; evidence stays on disk and real banks must never be committed (`guard` exists for that).

**Repo hygiene:** I wrote nothing into the repository. `git status` did show modified files (README.md, surfaces/cli.py, `.planning/` phase-17B/18 files, a `course_fixture_17b/` directory) with mtimes minutes into my run — another session on this machine is actively editing the repo concurrently. None of those paths were touched by any command I ran; all my writes are under the scratchpad `cold-agent-run-2` directory.

## Points of confusion

1. **Practice-mode `hold` is undocumented in the README's agent-driver section.** A wrong `submit` in practice mode returns `action: "hold"` with `accepted: false` and the session does not advance; the README's driver recipe ("submit scores the response... and returns the next item") reads as if submit always advances. This cost me a 2-minute infinite-loop timeout and is the one thing most likely to wedge a naive agent driver.
2. **The next item after `submit` is nested under `next`, not `item`.** Discoverable, but the README never shows a submit response shape.
3. **`itembank spec` numbers its item types 1-6, then 8 (check), then 7 (visual)** — the numbered list is out of order and looks like a typo or a merge artifact.
4. **README says "eight types ship" and "seven item types" in different places** (the quick-start says "seven item types" in the opening summary; the Item types section says eight). capabilities.json does not list types at all, so the README is internally inconsistent on the count.
5. **Skill-count mismatch:** README's agent section says "this repository ships five playbooks"; capabilities.json lists ten skills. (The README elsewhere does not explain which of the ten are stubs; that explanation lives in files I was forbidden to read.)
6. **`report` on a finished practice sitting still says `status: "active"`.** Correct per the documented short-item contract, but a newcomer looking for "done" must know to read `pending_manual` instead — the README does say this, buried in one paragraph.
7. Minor: the `start` output is extremely verbose (a full selection `trace` with a per-item justification sentence repeated seven times), which is a lot for an agent to wade through to find `item`.
8. Not the tool's fault, but worth recording: two of my own shell mistakes (zsh `=`-expansion on `echo ===`, and unsplit `$IB`) produced failures that could be misattributed to itembank by a careless agent.

**Verdict:** Yes — a newcomer agent can complete onboarding from the README (plus `spec` and capabilities.json) alone; every step succeeded on the first or second try, and the only real trap is the undocumented practice-mode `hold` action in the JSON submit loop.

## Executor notes on the run-2 confusions

Points 1, 2, 4, and 5 became README fixes 6 to 8 above. Point 3 is N-01
and point 7 is N-03 under Named defects. Point 6 is the documented
contract working as written. Point 8 is the agent's own shell, recorded
for honesty. Run 2's command-count reading (53) differs from run 1's (50)
and from 18-02's recorded 52 because a concurrent session was editing
`surfaces/cli.py` during both runs; the counts were read from the live
parser at different moments and none of them is this transcript's claim.
