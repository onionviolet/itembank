# Pitfalls Research

**Domain:** Local-first learning platform with an LLM authoring/auditing layer (itembank v-next: evidence redesign, lesson format, Socratic hint ladder, code-executing items, objective-level scheduling, LLM auditor with write access, trend-driven selection, packaging, self-updater)
**Researched:** 2026-08-05
**Confidence:** MEDIUM (LLM-generated-content failure modes and the content-addressing/evidence-reset pattern are backed by peer-reviewed and directly-analogous prior-art sources at MEDIUM confidence; scheduling-conflict, migration, self-updater, and scope-failure claims are backed by community/issue-tracker sources at LOW confidence and are triangulated against this codebase's own documented anti-patterns and concerns, which is why they are still actionable)

## Critical Pitfalls

Ranked by how much damage they do if undetected and by dependency — earlier pitfalls block or corrupt everything downstream of them (evidence spine feeds trends, scheduling, and the auditor; auditor autonomy gates everything the auditor touches).

### Pitfall 1: Content-hash item IDs silently orphan evidence history on every edit

**What goes wrong:**
The evidence spine requirement (`PROJECT.md` Active, "Evidence spine") calls for "stable content-hash item IDs, immutable after first lint, replacing positional `Qn`." A content-derived ID is stable only while the content is byte-identical. The moment anyone — a human fixing a typo in a stem, `lint` normalizing whitespace, or the new auditor "absorbing" a correction — edits an item, its hash changes, its ID changes, and every piece of evidence keyed to the old ID (attempt history, hint-tier-reached, decay flags, objective accuracy trend) stops being about "this item" and starts being about a phantom item nobody will ever see again. This is not hypothetical: it is the *documented, accepted trade-off* of the closest prior-art system (a plain-text, content-hashed spaced-repetition format), whose own author states plainly that editing a card resets its learning history because the card is identified by the hash of its text.

**Why it happens:**
Content-hashing is attractive because it is deterministic, requires no coordinator, and plays well with git — exactly the properties this project already values (`itembank guard`, synthetic fixtures, plain markdown). The failure mode is invisible at design time because "immutable after first lint" reads as a guarantee, not a constraint: it guarantees the ID *won't* change only if the content never does, and this project's own material (`da` per-option rationale, 25 of 45 wrong options currently missing the "would be correct when" clause) is explicitly expected to be edited during this milestone.

**How to avoid:**
Separate "identity" from "content fingerprint." Assign a stable, opaque ID at first lint (a UUID or a counter, not a hash) and store the content-hash *alongside* it as a change-detection field, not as the key. Evidence records key off the opaque ID. When content changes, the opaque ID persists and the hash field updates — this is exactly the distinction `runtime.py`'s existing `SESSION_VERSION` pattern almost has (a version number that doesn't reset identity) but the schema-migration gap flagged in `CONCERNS.md` ("no migration logic... old session files will fail to load") shows this codebase does not yet have a working precedent for evolving an identifier under live data. If a content-hash *is* kept as the literal ID (matching the explicit requirement wording), then the evidence store must also store an explicit rekey/alias table (`old_id -> new_id`, with a reason and timestamp) written automatically whenever `lint` detects an ID collision-by-similarity, so "how am I doing on this objective over time" does not quietly reset every time an item is corrected.

**Warning signs:**
- An objective's accuracy trend has unexplained gaps or restarts to zero shortly after a bank was edited.
- `git log` on a bank file shows content edits with no corresponding entry in an ID-remap log.
- The decay-flagging feature ("correct a month ago, untouched since") never fires for an objective that both was edited during the milestone and had prior evidence — because the "correct a month ago" record is now attached to an ID nothing points at.

**Phase to address:**
Evidence spine phase — before the auditor or trends phases, exactly as `PROJECT.md`'s own Key Decision already orders it ("Evidence spine (#4) and daemon (#7) before the auditor and trends... building them before stable IDs and one store means building them twice"). This pitfall is the concrete failure that decision is protecting against; make the rekey/alias mechanism (or opaque-ID-plus-hash split) an explicit acceptance criterion of that phase, not an assumed side effect of "content-hash IDs."

---

### Pitfall 2: The auditor confidently declares curriculum coverage that doesn't exist

**What goes wrong:**
This is the founding failure recurring one layer up. The original incident was an AI inventing its own item format and nothing noticing for days. The auditor requirement — "ingest a syllabus... extract objectives, including subtleties, not just headings" and "map extracted objectives against bank coverage and report what has no items" — hands an LLM the job of being the feedback signal for coverage itself. Research on LLM calibration is consistent and specific here: RLHF-tuned models are systematically miscalibrated such that the *highest*-confidence outputs are disproportionately where they're wrong, and curriculum/standards-tagging performance is documented to degrade specifically on frameworks that are local or under-represented in training data — which describes this project's actual objectives (an EMT bank derived from AAOS 12e, a specific Math 1400 syllabus, a specific CSCI 1100 course) far better than it describes a well-known public standard like Common Core. An auditor can therefore report "objective X: covered" with high apparent confidence while having matched on a heading's wording and missed the syllabus's subtlety underneath it — the exact "invented its own format, nothing noticed" shape, replayed as "invented its own notion of coverage, nothing noticed."

**Why it happens:**
Coverage-mapping is a matching-and-inference task over a domain-specific, low-resource document (one professor's syllabus), which is precisely the condition under which LLM tagging accuracy is documented to drop. There is no existing "coverage lint" in this codebase to catch it the way `model.lint()` catches a malformed item — coverage claims are semantic, not structural, so the tool's existing "fail fast and loudly with actionable messages" philosophy (`ARCHITECTURE.md`, Error Handling) has nothing to hook into yet.

**How to avoid:**
Treat every auditor coverage claim as a hypothesis requiring an inspectable trail, never a verdict. Require the auditor to emit, per objective, the *exact syllabus passage* it matched against and the *exact bank item(s)* it counted as coverage — a citation, not a conclusion — and make "no citation" a hard lint-equivalent failure of the audit output itself (mirroring how `model.lint()` refuses to pass an item silently). Report-only autonomy should be the default and the longest-lived mode in practice regardless of what the config allows, and "gap reported" should be trusted far more than "coverage confirmed," since a false negative (missed gap) is cheap to catch later and a false positive (false confidence of coverage) is not caught until the exam.

**Warning signs:**
- Audit output states a coverage percentage or verdict without a quoted syllabus excerpt and item ID pair for every claim.
- Coverage claims correlate with heading text overlap (objective titled the same as a section header) more than with item content.
- The auditor's confidence language ("fully covered," "well covered") doesn't vary with how many items actually support the claim.

**Phase to address:**
The auditor phase — and specifically before autonomy is allowed past report-only. Make "every coverage claim carries a citation" a structural output-contract requirement (like the JSON schema requirement already planned for the agent interface), not a prompt instruction, so it can be validated the same way `lint` validates item format.

---

### Pitfall 3: Full auditor autonomy (audit-draft-lint-fix-commit) causes rubber-stamped drift, not caught mistakes

**What goes wrong:**
`PROJECT.md` already flags this decision `⚠️ Revisit`: "The auditor may generate items, bounded by lint and reversibility... it survives only because every generated item passes the same contract a human's does, and every write can be undone." The problem is that `lint` checks the *format* contract, not truth — a wrong-but-well-formed item, or a hallucinated-but-plausible coverage claim (Pitfall 2), sails through `lint` clean. Research on agent approval fatigue is unambiguous about the failure mode at the top of the autonomy range: when a human is asked to approve a stream of agent actions, oversight collapses into rubber-stamping once volume exceeds review bandwidth, and a bad action hidden inside a batch of routine-looking ones is the one that gets through — not because the reviewer is careless, but because approval-as-attention doesn't scale to volume the way approval-as-boundary does.

**Why it happens:**
"Every write is reversible" (a git revert) answers "can we undo it" but not "will we notice we should." Reversibility is a recovery property; it does nothing to prevent the silent-drift window between a bad auto-commit and someone noticing, which for a bank that's mostly reviewed under exam pressure (EMT, Math 1400, CSCI 1100 coursework) could be exactly the multi-day gap the founding incident had.

**How to avoid:**
Autonomy should be a graduated boundary, not a single knob defaulting to "full" for convenience. Concretely: full audit-draft-lint-fix-commit should require a *second*, independent, cheap check beyond `lint` before auto-commit is allowed — e.g. a distractor-plausibility pass (see Pitfall 4) and a diff size/velocity cap (no more than N items auto-committed per run without a human checkpoint) — because the research-documented fix for approval fatigue is precise autonomy tiers with automated classifiers doing the routine approvals, leaving only genuine exceptions for a human, not a human asked to read everything the agent did. One-item-per-commit (not batched commits) keeps `git revert` cheap and keeps a human's spot-check of `git log` actually legible.

**Warning signs:**
- Bank diffs from auditor commits grow large enough that nobody actually reads them before the next session.
- The autonomy setting is left at "full" past the milestone that introduced it, because nothing has visibly gone wrong yet — which is exactly what silent drift looks like from the inside.
- Auditor commits and human commits become indistinguishable in `git log` (no tag, no distinct author, no commit-message convention marking machine-authored changes).

**Phase to address:**
The auditor phase. Ship report-only and draft-and-approve fully before full autonomy is even wired up; require distinct commit authorship/tagging for auditor writes as a phase acceptance criterion, so `git log` itself becomes the audit trail this pitfall needs.

---

### Pitfall 4: LLM-generated items pass `lint` while failing as items — implausible distractors, answer-leaking stems, near-duplicates

**What goes wrong:**
`model.lint()` enforces the format contract (fields present, types correct, the `da` "would-be-correct" warning), not item quality. Peer-reviewed evidence on AI-generated multiple-choice items is consistent: LLM-authored items show lower discrimination than human-authored ones and reproduce "novice item-writer" flaws — non-functional (implausible) distractors, and specific cueing patterns such as longest-option-is-correct, absolute-language distractors, and word/phrase repetition between the stem and the correct option (a stem that leaks the answer through vocabulary overlap). A 2026 study specifically measuring AI-*assisted* workflows found the presence of an AI drafting step increased item-writing flaws that reached final content *because of automation bias* in the human reviewers, not despite review — reviewers trusted the draft more, not less, because it looked well-formed. None of this is caught by a format linter, because these are quality properties, not structural ones.

**Why it happens:**
This project's own authoring analysis already shows the raw material has this exact shape at human scale — 25 of 45 wrong options in a live EMT bank lack the "would be correct when" clause `lint` warns about, and *zero* lack a line entirely. An LLM asked to write toward that pattern will reproduce "always has *a* line, often not a *good* line" faster and at higher volume, because that's the statistical shape of the training signal on this exact bank, and lint's existing check (line exists) will not catch it.

**How to avoid:**
Add a distractor-quality pass distinct from format `lint`, at minimum: (a) flag any option whose text has high token overlap with the stem or with the correct answer's rationale (a proxy for answer-leakage and vocabulary cueing); (b) flag stems/options using absolute language ("always," "never," "only") disproportionately on distractors vs. the key; (c) flag near-duplicate items within a bank by stem similarity, since a closed authoring loop retried to a "clean" state can regenerate a semantically identical item under a different content-hash (compounding Pitfall 1); (d) keep the existing `da`-missing-rationale warning but raise it from warning to a *blocking* check for machine-authored items specifically, since "authoring is a gap, not a blocker" was true for human-authored content but an LLM given the same green light will not close that gap on its own — it will match the existing gap rate.

**Warning signs:**
- Auditor-generated items pass `lint` at a noticeably higher clean-rate than human-authored items in the same bank (a sign quality checks aren't running, not that the AI is better).
- Distractors across generated items reuse similar phrasing ("commonly confused with," "a related but incorrect concept") — a template tell.
- Two items in a bank test the same discriminator with different surface wording (near-duplicates) after several closed-loop authoring runs.

**Phase to address:**
The teaching-loop / authoring phase where the closed authoring loop (spec, draft, lint, retry-to-cap) is built (#11). Build the quality pass as a second gate in that same loop, before the auditor phase reuses it for autonomous commits.

---

### Pitfall 5: Overstating what learner-code execution actually protects against

**What goes wrong:**
The `check` item type runs the learner's own code and compares output — explicitly "scoped to running the learner's own answer, no sandboxing claim" per the Key Decisions table, and `CONCERNS.md` already documents that this codebase's existing subprocess usage (`day.py` git/editor calls) has unescaped, injectable paths. Research on Python-level sandboxing is blunt: running untrusted code in a plain subprocess still shares the host's filesystem, network, and resources, and does not bound CPU, memory, or wall-clock time without additional OS-level tooling; language-level restriction tricks (blocking `import os`, restricted builtins) are documented as reliably escapable via introspection (e.g., reaching `subprocess.Popen` through `object.__subclasses__()`) even when the obvious dangerous names are blocked. The honest posture is: a bare `subprocess` call with a timeout stops an *accidental* infinite loop; it does not stop a *deliberate* malicious payload, and CTF-style writeups of exactly this kind of Python "sandbox" escape are common enough to be a well-trodden genre.

**Why it happens:**
It's tempting to read "no sandboxing claim" as already-solved because it disclaims the promise, but the danger is in what gets built anyway: a timeout, maybe an output-size cap, and the natural next step of trusting that combination more than it deserves because it feels like enough for a single-user local tool. The actual risk profile for this project is genuinely low (the learner is the only one who can plant a payload for their own machine) but "low risk" and "no exposure" are different claims, and the difference matters the moment `check` items are shared, exported, or the auditor is asked to *generate* a `check` item's reference solution/verifier itself — at which point the trust boundary is no longer "the learner attacking themselves."

**How to avoid:**
State the security posture in the format contract and the code itself, not just in `PROJECT.md`: a subprocess timeout and a working-directory scope prevent *accidents* (infinite loops, runaway output, writes outside the sandbox directory if enforced via a temp cwd); they do not prevent a *deliberate* escape, and this tool must never execute code it did not get directly from the person sitting at the keyboard — not from an imported bank, not from the auditor's generated verifier without human review, not from a shared/downloaded bank file. Enforce a hard wall-clock timeout with process-group kill (not just the immediate child, since a forked/spawned grandchild can outlive a naive `Popen.kill()`), run in a throwaway temp directory, and do not attempt to claim filesystem or network isolation the mechanism doesn't provide.

**Warning signs:**
- A roadmap or UI copy describes `check` items as "safe" or "sandboxed" rather than "runs locally, no isolation."
- The auditor is given authority to write `check`-type verifier code without a human review step distinct from `lint`.
- Timeout kills the visible child process but a spawned grandchild process is still observed running afterward.

**Phase to address:**
The teaching-loop phase that introduces `check` (#13). Write the honest security note into the format `spec` output itself (the way `spec` already documents the format contract) so an authoring agent — human or AI — reads the actual boundary, not an assumed one.

---

### Pitfall 6: Two "due" systems disagree, and nobody owns the tiebreak

**What goes wrong:**
Anki keeps owning card reviews; itembank adds objective-level scheduling on top, by design (`PROJECT.md`: "One scheduler and no second card store... a deeper Anki merge is a v2 question, not an assumption"). But `day.py` already recomputes Anki due/new counts per lane on every page render (`CONCERNS.md`, Performance Bottlenecks), and this milestone adds a second, independent notion of "due" — objective-level, evidence-driven, decay-flagged, hint-tier-aware — that reads a different store and uses a different definition of "mastered." Anki's own ecosystem shows this exact class of failure when two systems both claim ownership of interval/due-date state: add-ons or schedulers that modify due dates independently of the active scheduler produce conflicting due dates and a disrupted review queue, and the documented fix in that ecosystem is explicitly "don't run two things that both think they own this," not "reconcile them after the fact." itembank's situation is a step more subtle because the two systems don't touch the same field (card intervals vs. objective weight) — but a learner experiences "what should I do today" as one question, and `day`'s cockpit is exactly where both answers will land side by side.

**Why it happens:**
"Anki owns cards, itembank owns objectives" is a clean line on paper, but an objective and its cards are the same underlying material from the learner's point of view, and the two evidence sources (Anki review history vs. itembank's hint-tier-aware response history) can and will disagree about whether something is "known" — Anki says a card is due because its interval elapsed; itembank's decay flag says an objective is at-risk because it was untouched for a month; these can point at the same material and give different urgency signals with no arbiter.

**How to avoid:**
Make the disagreement visible and explicit rather than silently resolved: `day`'s load/behind computation and the new `/report` view should show Anki-due and itembank-decay as two labeled signals, not merge them into one number. Cache the Anki query result itbank already needs to fix for performance reasons (`CONCERNS.md` already flags this as a bottleneck to fix) *once* per render and pass it to both the existing lane-load computation and the new evidence-driven "what's due" computation, so at minimum they're reading a consistent snapshot rather than racing each other across two separate queries in the same page load.

**Warning signs:**
- `day` cockpit and `/report` show different "you're behind on X" signals for the same objective in the same session.
- Evidence-backed `load` (the new requirement extending `day`'s existing number) is computed from a stale or differently-timed Anki snapshot than the lane `behind` calculation already on that page.
- A learner's daily cap gets consumed by itembank-selected review of material Anki *also* just reviewed minutes earlier, because neither system checked the other's recent activity.

**Phase to address:**
Retention-and-pacing phase (#18 area), after the evidence spine lands. Treat "one snapshot, two labeled views" as an explicit acceptance criterion, not an implementation detail.

---

### Pitfall 7: 45 requirements in one milestone reintroduces the big-bang-rewrite failure shape

**What goes wrong:**
This milestone's own framing acknowledges the risk ("Scope is deliberate; sequencing carries the risk") but scope this large — evidence redesign, a lesson format, a hint ladder, code execution, scheduling, an LLM auditor with write access, trend-driven selection, packaging, and a self-updater — has the structural signature of what's documented as a "big-bang" build: unlike a greenfield rewrite, it has a floor (everything the tool already does — six item types, deterministic scoring, `day`, export — must keep working throughout, per the "format changes must be additive" constraint), and every new capability gets added on top of that floor rather than replacing anything, which is exactly the pattern documented to blow timelines past estimate by a wide margin, because there's no point at which shipping less is actually an option once the floor is committed to.

**Why it happens:**
Each individual piece here is well-reasoned and sequenced correctly relative to its neighbors (evidence-before-auditor, evidence-before-trends is explicitly decided), but sequencing correctness between features is different from having real, independently shippable checkpoints. A plan can be correctly ordered and still be a single 45-requirement critical path if no phase boundary is a place the project could stop, use what exists, and still have gained something.

**How to avoid:**
The mitigation this class of failure responds to in the research is concrete and already partially present in this project's own phase-transition discipline (`PROJECT.md`'s "Evolution" section, `/gsd-transition`): make every phase boundary a genuine usable checkpoint, not just a milestone-internal task boundary. Concretely for this roadmap: the evidence spine phase should leave the *existing* surfaces (quiz, study, day) fully working against the new store before any new-capability phase starts — i.e., migration-and-parity is its own checkpoint, not folded into "evidence spine done." The auditor's report-only mode is a real, shippable, useful checkpoint on its own, well before draft-and-approve or full autonomy — ship it as one. `check` items and the hint ladder are independently valuable without the auditor or trends being done at all.

**Warning signs:**
- A phase plan for "evidence spine" implicitly includes half of "the teaching loop" because they touch overlapping files.
- No phase in the roadmap has a UAT/demo that doesn't depend on a phase not yet built.
- Time estimates for later phases (auditor, trends) keep sliding because earlier phases (evidence spine, daemon) aren't fully closed out before work starts on them.

**Phase to address:**
Roadmap structure itself — this is a pitfall for the roadmapper, not a single implementation phase. Each phase should close with a working, demoable state using only what exists at that point.

---

### Pitfall 8: The self-updater is asked to replace the process running it

**What goes wrong:**
The plan is a stdlib `python -m zipapp` artifact self-updating against GitHub Releases with checksum verification and atomic replacement. Two things the research surfaces are easy to under-specify: first, checksum verification (comparing a downloaded asset's sha256 against a published digest) protects against corruption and network tampering, but if the digest is published on the *same* channel as the release itself, it does not protect against a compromised or malicious release — that requires a signature verified against a key distributed out-of-band, which is a materially bigger undertaking than "compute sha256 and compare," and the requirement as written ("checksum verification") should not be read as equivalent to authenticity verification. Second, atomically replacing a running `.pyz` while the process that *is* that file is still executing runs into the same category of problem self-update libraries in compiled languages solve with a separate relaunch step: most platforms (Windows especially, given this project's stated OS) will not let a process overwrite or delete its own running executable file, so "atomic replace" needs a write-to-new-path-then-relaunch design, not an in-place overwrite.

**Why it happens:**
"Checksum verification and atomic replacement" reads as a complete, closed spec, but each half is doing less than it sounds like: checksum answers "did the bytes arrive intact," not "should I trust these bytes," and "atomic" in filesystem terms (write temp, `os.replace()`) is a pattern this codebase already uses correctly for session writes (`runtime.py`) but that pattern assumes the file being replaced isn't the one currently executing.

**How to avoid:**
Scope the checksum verification claim honestly: it catches transport corruption, not a compromised release — call that out explicitly in the settings/config documentation the way the network-constraint narrowing is already called out explicitly in `PROJECT.md` ("so a future session does not reason 'it runs offline, so it's fine'"), and treat the downgrade-attack case explicitly: reject a downloaded "update" whose version is not strictly greater than the running version, even if its checksum is valid, since a valid-but-old signed/checksummed asset is exactly what a downgrade attack replays. For the running-process problem, download to a side-by-side versioned path, verify, then have the *current* process exit and hand off to a tiny launcher (already planned as a per-OS one-line launcher) that points at the new path on next start — don't attempt to overwrite the currently-executing file.

**Warning signs:**
- The updater's "atomic replace" step is implemented as writing directly over the currently-running `.pyz` path.
- No version-monotonicity check exists — any checksummed asset from the releases feed is accepted regardless of whether its version is older than what's installed.
- Update failures leave no old version reachable (no side-by-side retained copy to fall back to if the new version won't launch).

**Phase to address:**
Packaging/settings/updates phase, at the end of the milestone per the existing plan — but design the launcher hand-off and version-monotonicity check as acceptance criteria of that phase, not follow-on hardening.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|-----------------|------------------|
| Content-hash IS the item ID (no separate opaque ID + alias table) | Simpler schema, matches the literal requirement wording, no rekey logic to write | Every content edit orphans evidence history (Pitfall 1) | Only if items are treated as append-only/immutable post-lint in practice — i.e., corrections create a *new* item and the old one is explicitly retired, never silently "fixed in place" |
| Trusting `lint`-clean as "auditor-generated item is good enough to auto-commit" | Fast closed authoring loop, no added review step | Ships plausible-looking but low-discrimination or answer-leaking items at scale (Pitfall 4) | Never for full-autonomy commits; acceptable for draft-and-approve where a human still reads before commit |
| `check` timeout-only "sandboxing" | Cheap, stdlib-only, matches the "no dependency" constraint | Silent overclaim if UI/docs later drift into calling it safe (Pitfall 5) | Acceptable indefinitely for a genuinely single-user local tool, provided the posture is documented honestly and code never arrives from anyone but the keyboard user |
| Auditor commits batched (many items per commit) for throughput | Fewer commits, faster runs | Makes `git revert` (the stated reversibility guarantee) an all-or-nothing operation, raising the cost of catching one bad item late | Never once autonomy passes draft-and-approve; fine while still human-approved per item |
| Reusing `day.py`'s existing Anki-query-per-render pattern for the new evidence-driven "due" computation | No new caching code to write | Compounds an already-flagged performance bottleneck (`CONCERNS.md`) and risks Pitfall 6's snapshot-mismatch | Never — this is exactly the code path already flagged for a fix; fix it once, for both consumers |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|-----------------|-------------------|
| Model adapter (Claude Code / Codex / competitor / future local Qwen) | Assuming one uniform request/response/error/rate-limit contract across vendors and baking vendor-specific quirks into caller code | Normalize errors, retries, and rate-limits *inside* the adapter interface so callers (`hint`, `short` rubric marking, the auditor) never branch on which vendor answered — matches the existing "interface, not a vendor" decision |
| GitHub Releases self-updater | Trusting the release feed's own tag/asset as both the version source and the trust source, with no monotonicity check | Compare parsed semantic version against the currently running version and refuse anything not strictly newer, independent of checksum validity (Pitfall 8) |
| AnkiConnect (existing, extended by scheduling work) | Re-querying Anki independently from multiple code paths on the same render (already the case in `day.py`; scheduling adds a second consumer) | One query per render, cached and shared between the lane-load computation and the new evidence-driven due computation (Pitfall 6); `CONCERNS.md` already recommends validating `ANKI_CONNECT_URL` is localhost-only — extend that same validation discipline to any new Anki read path |
| Local LLM backend (future, 7900 XTX hardware) | Building the adapter interface around cloud-vendor assumptions (network calls, hosted rate limits) that don't fit a local inference server | Design the adapter's contract now around request/response shape only, not transport assumptions, so a local backend is a drop-in implementation, not a redesign |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|-----------------|
| Evidence store rewritten in full on every response (matching the existing session-file full-rewrite pattern in `session.py`/`quiz.py`) | Noticeable lag on fast-answer sequences once evidence records more fields (response time, confidence, error category, review state — all explicitly planned to be captured) | Append-only evidence log (or `os.replace()`-based atomic write of only the delta) rather than full-file rewrite per response, following the one place that already does this right (`runtime.write_session`) | Once a single learner's evidence history spans months across three subjects — well within this project's real one-year usage horizon |
| Auditor re-parsing the whole bank and re-running coverage matching from scratch on every invocation | Audit runs that were fast on a 21-item bank become slow on a full-course bank across a semester | Incremental audit: only re-check objectives whose source syllabus text or bank items changed since the last run | As soon as one subject's bank grows past the size of the original 21-item bank that started this project |
| `day` cockpit computing Anki counts *and* the new evidence-driven due signal as two independent per-render queries | Page load time creeps as both scheduling systems query their sources on every render (compounding the already-flagged Anki bottleneck) | Single snapshot per render, shared by both computations (Pitfall 6) | Once lanes scale past the ~6 already flagged as a scaling limit in `CONCERNS.md`, or once trend/decay computations join the same render path |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Treating `check` item timeout as a security boundary rather than an accident-guard | A malicious or careless verifier/reference-solution (especially one the auditor generates) escapes the intended trust boundary — subprocess isolation does not confine filesystem, network, or resource use (Pitfall 5) | State the posture honestly in `spec`; never let generated code run without the human who will execute it having authored or reviewed it |
| Checksum-only update verification presented as sufficient trust verification | A compromised release channel can publish a valid checksum for a malicious asset; a downgrade to an old-but-validly-checksummed version is also accepted | Document checksum as integrity-only, not authenticity; add explicit version-monotonicity rejection (Pitfall 8) |
| Auditor given filesystem write access to the real (private) bank without commit-scoping | A bad auto-commit is technically revertible but only if it's discoverable and isolated — batched or unlabeled commits make "every write is reversible" true in principle and false in practice | One auditor-authored item per commit, clearly tagged authorship, autonomy gated below full for anything beyond report-only until a second quality gate exists (Pitfalls 3, 4) |
| Extending `ANKI_CONNECT_URL`-style remote-URL trust to any new integration point added for scheduling | `CONCERNS.md` already flags that a non-default `ANKI_CONNECT_URL` could send deck data over a real network, defeating the local-only guarantee | Any new network-capable config value (model adapter endpoint, update feed URL) gets the same localhost/allow-list validation discipline already recommended for `ANKI_CONNECT_URL` |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-------------------|
| Hint ladder gameable by rapid wrong-submission spam | A learner (or someone testing the tool) can descend tier 0→5 in seconds by submitting nonsense answers, defeating the entire "cannot reveal a tier it hasn't unlocked" design premise the milestone is built around | Gate tier advancement on a minimum engagement signal (a real second attempt, not an empty/repeat submission) or make hint-tier-reached itself a visible evidence field so gaming shows up in `/report` rather than being invisible |
| "Right at tier 1" vs "right at tier 4" distinction computed but not surfaced anywhere a learner or the trends system can see it | The design cost of building the distinction (a new `report` requirement) is paid but its payoff (decay flagging, selection weighting) is lost if it's buried in raw evidence rather than shown | Make hint-tier-reached a first-class, visible column in `/report`, not just an internal field feeding selection weights |
| Theme contrast/deuteranopia-safety computed only at OS-color-picker time, not re-validated if `theme.json` is hand- or agent-edited | A user or an agent (config is explicitly agent-writable per this milestone) can set an invalid/inaccessible theme directly in `theme.json`, bypassing the picker's guarantees entirely | `itembank config`'s planned validation ("lint rejects an invalid value") must cover computed-contrast fields, not just presence/type of theme keys |

## "Looks Done But Isn't" Checklist

- [ ] **Evidence spine:** "One evidence store" often ships as the only store *new* writes go to, while `_attempts/*.md`, session JSON, and `daily_log.md` history sits unmigrated and unreadable by the new store — verify a backfill/migration path exists, not just a new write path.
- [ ] **Content-hash item IDs:** Often ships without a tested "edit an existing item, confirm evidence history still resolves" case — verify this explicitly, since it's the one scenario the format is structurally weak against (Pitfall 1).
- [ ] **`LESSON-REF` linking:** Often ships without a lint check for a `LESSON-REF` pointing at a `LESSON` section that doesn't exist — verify it fails at `lint` time with an actionable message, not at render time with a `KeyError`, matching this codebase's existing "fail fast and loudly" pattern.
- [ ] **Closed authoring loop (#11):** "Passes `lint` after retries" often gets treated as "the item is good" — verify a distractor-quality/duplicate pass runs before anything is written to a real bank (Pitfall 4).
- [ ] **`check` item type:** "Compares output" often ships as one hardcoded expected-output string — verify it supports multiple test cases/edge cases, since a single string comparison is trivially gameable by a learner who prints the expected literal.
- [ ] **Self-updater:** "Ships" often means the happy path (download, verify, install) works — verify the failure path: what the app does on next launch after an interrupted or failed update (Pitfall 8), and that offline truly fails silently rather than blocking the page as the constraint requires.
- [ ] **Every capability reachable from both app and CLI:** Often ships with the CLI command built first and the route added as an afterthought that doesn't actually call the same runtime function — verify the route and the command share one implementation, not two that happen to agree today.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|----------------|------------------|
| Evidence orphaned by an item-ID change (Pitfall 1) | MEDIUM | Diff the bank's git history for the edited item, manually construct an old-ID→new-ID alias entry, backfill the evidence store's index; cost rises with how long the drift went unnoticed |
| Auditor committed a bad item (Pitfall 3/4) | LOW if one-item-per-commit; HIGH if batched | `git revert` the specific commit; recovery is only cheap if commit scoping (Pitfall 3's prevention) was actually followed |
| Self-update left a broken install (Pitfall 8) | LOW if side-by-side versions retained; HIGH if overwritten in place | Relaunch the previous version's retained path; if none was retained, the user is back to a manual reinstall from the release page |
| Two scheduling signals disagreed and a learner over- or under-reviewed (Pitfall 6) | LOW | No data loss — worst case is wasted review time; fix is a UI/labeling change (show both signals), not a data recovery operation |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|-------------------|----------------|
| Content-hash IDs orphan evidence (1) | Evidence spine | Edit an existing item's content post-lint; confirm its evidence history still resolves under the new ID or via an alias record |
| Auditor over-claims coverage (2) | Auditor — report-only stage | Every coverage claim in audit output carries a quoted syllabus excerpt and item-ID citation; spot-check a sample against the actual syllabus |
| Full autonomy causes rubber-stamped drift (3) | Auditor — before enabling full autonomy | Auditor commits are one-item, distinctly authored/tagged; a second quality gate beyond `lint` exists before full-autonomy is unlocked in config |
| LLM items pass lint but fail as items (4) | Closed authoring loop (#11), reused by auditor | Distractor-quality/near-duplicate pass runs and blocks on failure, distinct from and in addition to `model.lint()` |
| `check` overclaims isolation (5) | Teaching loop — `check` item type (#13) | `spec` output and any UI copy state the honest posture; process-group-safe timeout kill verified against a grandchild-spawning test case |
| Two "due" signals disagree (6) | Retention and pacing (#18) | `day` and `/report` show Anki-due and itembank-decay as separate labeled signals from one shared per-render snapshot |
| 45-requirement milestone big-bangs (7) | Roadmap structure | Every phase closes with a working, demoable state using only what's built so far; no phase's UAT depends on an unbuilt later phase |
| Self-updater replaces its own running process / accepts a downgrade (8) | Packaging, settings, and updates | Update writes to a side-by-side versioned path and relaunches via the launcher rather than overwriting in place; a downloaded asset with a version ≤ current is rejected regardless of valid checksum |

## Sources

- [Do Large Language Models Plan Answer Positions? Position Bias in Multiple-Choice Question Generation (arXiv 2605.01846)](https://arxiv.org/html/2605.01846v1) — MEDIUM confidence
- [Validity of AI-generated multiple-choice questions in medical education: a systematic review (Postgraduate Medical Journal, Oxford Academic)](https://academic.oup.com/pmj/advance-article/doi/10.1093/postmj/qgag057/8688271) — MEDIUM confidence
- [A suggestive approach for assessing item quality, usability and validity of Automatic Item Generation (Advances in Health Sciences Education, Springer)](https://link.springer.com/article/10.1007/s10459-023-10225-y) — MEDIUM confidence
- [AI-assisted MCQ creation increases item-writing flaws through automation bias (Frontiers in Computer Science, 2026)](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2026.1831250/full) — MEDIUM confidence
- [Psychometric properties and detectability of GPT-4o–generated multiple-choice questions (npj Digital Medicine, Nature)](https://www.nature.com/articles/s41746-025-02313-7) — MEDIUM confidence
- [Large Language Models in K-12 Education: Alignment with State Curriculum Standards (arXiv 2606.04846)](https://arxiv.org/html/2606.04846) — MEDIUM confidence
- [From Learning Resources to Competencies: LLM-Based Tagging with Evidence and Graph Constraints (arXiv 2605.28483)](https://arxiv.org/pdf/2605.28483) — MEDIUM confidence
- [Your Model Is Most Wrong When It Sounds Most Sure: LLM Calibration in Production](https://tianpan.co/blog/2026-04-20-llm-calibration-production-overconfidence) — LOW confidence
- [Approval Fatigue Is Breaking AI Agents. Execution Boundaries Fix It.](https://medium.com/@shreya_edulakanti/approval-fatigue-is-breaking-ai-agents-execution-boundaries-fix-it-6c46c6d512dd) — LOW confidence
- [Oversight Has a Capacity: Calibrating Agent Guards to a Subjective, Fatiguing Human (arXiv 2606.08919)](https://arxiv.org/pdf/2606.08919) — MEDIUM confidence
- [Six layers to sandbox untrusted Python — and the escape I missed](https://chs.us/2026/07/sandboxing-untrusted-python/) — LOW confidence
- [Running Untrusted Python Code — Andrew Healey](https://healeycodes.com/running-untrusted-python-code) — LOW confidence
- [Hashcards: A Plain-Text Spaced Repetition System](https://borretti.me/article/hashcards-plain-text-spaced-repetition) — MEDIUM confidence (directly analogous prior art; explicitly documents the content-hash-resets-history trade-off this project is about to adopt)
- [What spaced repetition algorithm does Anki use? / fsrs4anki add-on compatibility notes](https://faqs.ankiweb.net/what-spaced-repetition-algorithm) — LOW confidence
- [Why Big Rewrites Fail — Potapov.dev](https://potapov.dev/blog/why-rewrites-fail/) — LOW confidence
- [Why a "Big Bang" Rewrite of a System is a Bad Idea in Software Development](https://scalablehuman.com/2023/10/14/why-a-big-bang-rewrite-of-a-system-is-a-bad-idea-in-software-development/) — LOW confidence
- Migration issue trackers on primary-key/identifier changes breaking foreign-key references (Rails #33520, EF Core #11800/#25040, Postgres/MySQL migration threads) — LOW confidence, triangulated across multiple independent trackers
- This project's own `.planning/codebase/CONCERNS.md` and `.planning/codebase/ARCHITECTURE.md` (Anti-Patterns, Fragile Areas, Security Considerations sections) — direct primary source, HIGH confidence for what it documents about the existing codebase

---
*Pitfalls research for: itembank v-next (learning platform milestone)*
*Researched: 2026-08-05*
