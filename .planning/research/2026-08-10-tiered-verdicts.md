# Research: Tiered Verdicts — one scorer, several strategies, three authority levels

- **Date:** 2026-08-10
- **Answers:** Research Brief 2 §2 R4.1 through R4.7
- **Binding:** `.planning/PLANNING-DIRECTIVES.md` §4.1 (the runtime, not a model, decides
  what reaches the learner) and §4.2 (one parser, one scorer, one evidence store).
- **Lands in:** Extensibility Rule 8 (rewritten), Phase 5 SC, Phase 6.1 SC4, Phase 8
  SC4, Phase 9 SC8. Does **not** land as its own phase.
- **Status of the brief's hypothesis:** partially overturned. The tier table is right
  about the three methods and wrong about the mechanism. See R4.1.

---

## 0. Verified current behavior (read, not assumed)

Checked against `runtime.py`, `model.py`, `evidence.py`, `itembank.py`, `GRADING.md`.

| Claim in the brief | Verified? | Where |
|---|---|---|
| `score_response()` is canonical-string equality | Yes | `runtime.py:120-130`, three lines: `canonical_key`, guard, `==` |
| Constructed response returns `None`, never `False` | Yes | `canonical_response` returns `None` for `short` (`runtime.py:82`), `canonical_key` returns `None` (`runtime.py:106`), `score_response` guards on `key is None` |
| No model participates in any verdict | Yes, and enforced at runtime | `evidence.mark_event()` raises `ValueError` if `marker != "human"` (`evidence.py:1058-1062`) |
| Verdicts are dichotomous | Yes | `verdict = bool(verdict)`; `GRADING.md:112`; `itembank.py:27-29` |

Three facts the brief does not mention, and all three change the answers below:

1. **A mark is already a separate append-only event, not a mutation.** `mark_event`
   (`evidence.py:1035`) records a fact *about* a response event. The response's own
   `score` stays `None` forever, and `review_state` is computed at read time from
   `marks_by_event` (`evidence.py:1118`). Marking already lives outside the scorer.
2. **Per-criterion rubric results already have a schema slot, and it is already N
   booleans.** `mark_event(rubric=[{"point": str, "pass": bool}])`. R4.7's "one-way
   door" was walked through in Phase 1, in the right direction.
3. **A retracted mark returns the response to `pending`.** So "unaccepted" is already
   a stable, recoverable state, not an absence.

---

## R4.1 — The interface

### Verdict

**Reject "one `Strategy` per item type returning `(verdict, authority, detail)`."
Adopt a registered *normalizer*, and split tier 3 out of the scorer entirely.**

Two registries, not one:

```
runtime.NORMALIZERS: {item_type: (q, answer) -> str | None}
runtime.KEYS:        {item_type: (q)         -> str | None}

def score_response(q, answer):
    key = canonical_key(q)          # dispatches to KEYS
    if key is None:
        return None
    return canonical_response(q, answer) == key   # dispatches to NORMALIZERS
```

`score_response()` does not change. Not "changes rarely" — the diff for every strategy
in the roadmap is zero lines inside it. The two functions it calls become registry
lookups instead of `if`-chains (Extensibility Rule 2 requires that conversion anyway;
`canonical_response` is already a five-branch chain).

**Every tier-2 checker in the roadmap is expressible as a normalizer.** This is the
load-bearing finding and it was not obvious:

| Checker | Normalized response | Key |
|---|---|---|
| `check` code (Phase 5) | per-case outcome vector after running, e.g. `PPFP` | all-pass vector `PPPP` |
| Math equivalence (Phase 9) | agreement vector at N pinned sample points | all-agree vector |
| `visual` tolerance (Phase 6.1) | response snapped to the tolerance-quantized cell | key snapped by the same policy |

Tolerance is quantization; execution is normalization with a subprocess in it. Neither
needs its own comparison. One `==` survives literally: a reviewer opens `runtime.py`,
points at line 130, and every accepted verdict in the system is that expression.

### What structurally stops accretion into a second scorer

Four guards, in decreasing strength. The first is the real one.

1. **Return type.** A normalizer returns `str | None`. It cannot return a verdict, a
   tier, or an authority, because there is no channel for one. The brief's candidate
   interface fails here: `(verdict, authority, detail)` hands every strategy the power
   to decide, and then asks it not to. That is a second scorer with a promise attached.
2. **Authority is a property of the code path, not a declaration.** Reject "the
   strategy declares its own authority and the runtime honors that declaration."
   Instead: anything that reaches `score_response()` is accepted, because only
   reproducible things can reach it; anything that reaches an evidence mark with a
   non-human marker is pending, always. Two paths, two fixed authorities, nothing to
   declare and nothing to honor. A declaration is a thing a future strategy can lie
   about; a code path is not.
3. **Tier 3 is not a scorer strategy at all.** It has no key, so it has no `==`, so it
   has no business in a function whose job is one comparison. A model proposing a mark
   is a *mark proposer* on the `evidence.mark_event` side of the boundary, where the
   human-only guard already lives. Extensibility Rule 8's table should be redrawn:
   tiers 1 and 2 are strategies **of** the scorer; tier 3 is a peer of the human
   marker, outside it.
4. **A pinned test.** `T-R4-01`: assert `hashlib.sha256(inspect.getsource(
   runtime.score_response))` equals a recorded constant. Any phase editing the scorer
   fails a named test and has to argue for it in a plan rather than in a diff. Cost:
   nine lines in `tests/scoring_roundtrip.py`.

**Cost:** two dict registries in `runtime.py`; conversion of two existing `if`-chains
(no behavior change, provable by the existing `scoring_roundtrip` fixtures);
one test; zero new dependencies; zero new blocks; zero lint codes.

---

## R4.2 — The authority rule

### The candidate fails, and it is the wording that is wrong, not the tiering

Candidate: *a verdict may be accepted only if it is reproducible from the item and the
response alone, with no model in the loop and no clock.*

Tested against the two named cases:

- **`check` with a timeout.** Fails. A timeout is a clock, and a slow machine flips
  `True` to `False`. But the tier assignment is right — the fix is that **a timeout is
  not a verdict**. An expiry returns `None` with `error_category: "timeout"`, exactly
  the None-not-False discipline `score_response` already applies to `short`. Not-run
  and ran-and-failed are as different as not-marked and marked-wrong. With that fix,
  every verdict `check` actually produces is clock-free, and the rule holds.
- **Math random sample points.** Fails as literally worded, passes trivially once the
  points are *derived* rather than *drawn*. Seed from the item's existing
  `content_hash` (`model.py:265`): `seed = int(q["content_hash"][:8], 16)`. The points
  are then a pure function of the item, reproducible on any machine, and no seed field
  is needed anywhere. Sampling with a content-derived seed is not randomness, it is a
  deterministic spot-check the item defines.

### The rule to adopt

> **A verdict may be accepted only if re-running it on another machine, from the
> recorded item version and the recorded response alone, must produce the same
> verdict. No model, and no input that is not derivable from the item.**

Testable, and it is testable the same way for all three tier-2 checkers: run the
strategy twice in one test, once under a fixture that perturbs machine speed, locale,
and process ordering, and assert identity. Anything a strategy needs that the item does
not supply is a bug in the item, caught at lint, not a licence to be nondeterministic.

Two named lint codes fall out:

- `item.tolerance_unstated` (error) — a `visual` or Math item whose accept bounds are
  neither in the item nor in a versioned policy the evidence records.
- `item.no_normalizer` (warning) — an item type with no registered normalizer, so the
  author learns before the learner does. See R4.6(c).

**Note the standing tension with Phase 6.1 SC3**, which deliberately keeps tolerance
*private* (not served to the client). That is compatible, but only if the **policy
version is written into the evidence event**. A private policy that bumps silently
reinterprets every past verdict, which is a reproducibility failure wearing an
encapsulation costume. Extensibility Rule 4 already requires the strategy name in the
event; this adds the version.

---

## R4.3 — Tier 2, the checkers

**One interface, three implementations, no shared base class and no shared helper
module.** They share their signature and their contract (`(q, answer) -> str | None`,
deterministic from the item) and nothing else. Building a "Checker" abstraction over a
subprocess runner, a numeric sampler, and a geometric snap would be inventing kinship
that is not there; the interface is thin precisely because that is all the kinship
available.

**Does WeBWorK-style random-point evaluation count as deterministic when it samples?**
Not as usually implemented, and yes as we should implement it. WeBWorK draws points at
evaluation time; two runs can disagree on a pathological function. Deriving the points
from the item's content hash makes the sample a fixed property of the item, which also
means editing the item changes the hash, changes the points, and correctly invalidates
nothing (the old event still records the old strategy version). Phase 9 SC8 already
scopes this at "roughly 200 stdlib lines, behind one accept rule"; this specifies the
seed and nothing else.

**What makes a checker reproducible across machines.** Ranked, and the ranking matters
because two of the three candidates in the question are weaker than they look:

1. **Bounds stated in, or derived from, the item.** Strongest. Travels with the
   content, is versioned by `content_hash` for free, and needs no evidence field. This
   is the primary mechanism.
2. **Strategy name and version recorded in the event.** Necessary but not sufficient.
   It does not make a result reproducible; it makes a past result *interpretable*,
   which is what you need when the policy changes. Required by Extensibility Rule 4.
3. **A seed recorded in the evidence.** Weakest, and the one to avoid. Recording a
   drawn seed makes history auditable while leaving the future nondeterministic, and it
   adds a field whose absence in old events becomes a permanent special case. Derive
   the seed instead of recording it.

---

## R4.4 — Tier 3, the model

Literature searched 2026-08-10. **Provenance warning: a large share of the sharpest
2026 numbers below are arXiv preprints that are not peer reviewed, and several cite
model names not independently verified. They are cited as the current state of a
literature, not as settled results.**

### What the evidence actually says

**LLM-vs-human agreement on short constructed response spans κ/QWK 0.00 to 0.95, and
the task predicts the number better than the model does.** Central mass 0.60 to 0.85.

- Henkel et al., reading comprehension (arXiv:2310.18373, 2023): GPT-4 few-shot QWK
  **0.92** against a human-human ceiling of **0.91**.
- A 32,534-response double-marked GCSE benchmark (arXiv:2606.24973, Jun 2026): English
  **0.75** vs examiner-vs-examiner **0.65**; Maths 0.86 vs 0.84; Science 0.74 vs 0.69.
  Frontier hosted models only; no open-weight models tested.
- Jiang & Bosch (L@S 2024) on ASAP-SAS: GPT-4 QWK **0.610**, rising to **0.677** with
  exemplars. The most-cited untuned figure.
- S-GRADES across 14 ASAG datasets (arXiv:2603.10233, Mar 2026): mean QWK **0.34 to
  0.43**. GradeRAG (EDM 2025) on NGSS science: Cohen's κ **0.000 to 0.331**.
- Same-study reversal: K-12 GenAI graders (arXiv:2606.12422, 2026) get Math QWK
  **0.951** and ELA written expression **0.393 to 0.495**.

Three findings matter more to this project than the headline range:

1. **Agreement is inflated by easy extremes and collapses in the middle.**
   arXiv:2605.07647 (2026, Hebrew biology) finds every model degrades badly on
   mid-range partially-correct responses (mean L1 error above 2 categories) while the
   human expert does not. Aggregate QWK overstates accuracy exactly where marks are
   contested. This is the single most important number in the whole search, and it is
   an argument against partial credit (R4.7), not just against auto-accept.
2. **LLM judges are not reproducible, even at temperature 0.** At provider-default
   temperature, per-item disagreement on borderline items reaches ~50% over 20 runs;
   even at temp 0 with top_k=1, 1 to 2 of 7 borderline items remain non-reproducible
   (arXiv:2606.26185, Jun 2026) because of batch-dependent float reduction order, MoE
   routing, and provider load balancing. **A tier-3 verdict therefore fails R4.2's rule
   on a technical ground, independent of §4.1.** Even if the policy allowed it, the
   physics does not.
3. **Documented bias survives explicit instructions not to be biased.** TOEFL11,
   12,100 essays (arXiv:2607.14605, Jul 2026): systematic L1 offsets within every
   proficiency band, German +0.55 SD and Korean/Japanese −0.34 SD, not explained by
   training-data representation. arXiv:2603.18765 (Mar 2026): informal-language penalty
   d = 4.25 and non-native-phrasing penalty d = 2.30 on identical substance,
   **persisting despite explicit anti-bias prompt instructions**. Blind grading does not
   fix it, since GPT-4o infers L1 from essay text at 0.75 to 0.87 accuracy
   (arXiv:2504.21330).

**Rubric decomposition: the accuracy case is not made.** For it: TICK (arXiv:2410.03608,
Oct 2024) 46.4% to 52.2% exact agreement; Branch-Solve-Merge (NAACL 2024) up to +26%;
RocketEval (ICLR 2025) gets Spearman 0.965 out of a 2B model with instance-specific
checklists; "Rubric Is All You Need" (ICER 2025) κ 0.156 to 0.646, though that is rubric
*specificity*, confounded with decomposition. Against it: the only prompt-controlled
study (arXiv:2603.28005, Mar 2026) finds holistic **matches or beats** atomic on 2 of 3
benchmarks once prompt richness is held constant; Decomposition Dilemmas (NAACL 2025)
finds it helps weak verifiers and *hurts* strong ones; holistic QWK 0.601 vs analytic
0.321/0.414 (arXiv:2604.00259, Mar 2026).

**Could not determine, and it is the exact question asked:** there is no within-task,
same-data, same-human-labels A/B of decomposed versus holistic rubric grading in
educational assessment. Every pro-decomposition result transfers from open-ended
generation evaluation. Also undetermined: any quantization-versus-judge-agreement study
(directly relevant to a 24GB local judge), and human-human QWK per prompt for ASAP-SAS.

**Self-assessment has the best evidence in the whole search, and it is pedagogical
rather than metrological.** León, Panadero & García-Martínez (2023), *Educational
Psychology Review*, meta-analysis of 160 articles, N = 29,352: learners overestimate by
g = 0.206 (small) and self-expert association r ≈ 0.44; overestimation shrinks with
feedback and content knowledge. As an intervention: self-explanation g = 0.55 (Bisra et
al. 2018); self-grading g = 0.34 (Sanchez et al. 2017); and decisively, Yan, Wang, Boud
& Lao (2023) find self-assessment **g = 0.664 with external feedback versus g = 0.213
without**. Four independent literatures converge on the same shape: self-assessment
alone is mediocre, self-assessment coupled to an external accuracy signal is good.

**Regulatory.** Ofqual, *Principles of AI use in marking*, 14 January 2026, reaffirmed
16 July 2026: "use of AI as the sole mechanism for determining a student's mark does not
comply with Ofqual's regulations." §4.1 is not an idiosyncrasy of this project; it is
the regulated position in the jurisdiction whose exams this most resembles. Texas STAAR
is the live counterexample (engine scores all constructed response, ≥25% routed to
humans); in 2025 Dallas ISD requested rescores and about a third of scores went up.

**Local models.** Open-weight judges at 8B to 32B lose roughly 0.02 to 0.05 Cohen's κ
against the best frontier on general judging (arXiv:2606.19544, Jun 2026: DeepSeek V3.2
0.486 vs Gemini 3.1 Pro 0.511), much more on open-ended rubrics than on closed
verification. Fine-tuned tiny models beat GPT-4o in-domain and collapse out of it (κ²
0.96 vs 0.93 in-domain; 0.31 vs 0.67 cross-domain). Quantization effects on judge
agreement are entirely unmeasured; adjacent evidence says prefer Q8/Q5 at ~30B and avoid
aggressive quantization of sub-8B judges.

### Ranking

On **promotability to `accepted` without a human, all four score zero.** That column is
not a spectrum; it is a constant, fixed by §4.1, by Ofqual, and independently by the
non-reproducibility result. Ranking is therefore on reliability and on how much useful
work each does.

| Rank | Approach | Reliability | Verdict |
|---|---|---|---|
| **1** | **Self-assessment against a revealed model answer** | r ≈ 0.44 as measurement; g = 0.55 / 0.664 as learning | **Ship as the default tier-3 path.** It is the only option that is a *learning* intervention as well as a marking one, and it dissolves the problem: a learner self-mark **is** a human accept, so there is no pending state to promote. Tier 3 stops being a gap and becomes a loop. |
| **2** | Deferred human marking | Ceiling by definition | Already built (`mark_event`, `itembank mark`). Keep as the fallback for anything the learner defers. This is what the tool does today and it is not wrong, only slow. |
| **3** | Rubric decomposition into independently-checkable claims | Accuracy gain **not established** for education | **Adopt, but justify it on accept ergonomics, not accuracy.** Per-criterion booleans are individually acceptable and individually rejectable, which is exactly what the accept flow needs, and they already have a schema slot. Do not claim, anywhere in the docs or UI, that decomposition makes the model more accurate. |
| 4 | Hand the whole answer to a model, holistic | Comparable QWK, sometimes better | Worst on promotability (nothing to accept piecemeal) and worst on auditability. Not shipped as a primary path; permitted as one proposal shape. |

**Ship both, per Directive §3, behind the named interface `MarkProposer`:** #1 and #3
are both good and they compose (self-mark first, model proposal as a second opinion).
The setting is R4.5's `suggestion_reveal`.

---

## R4.5 — Presentation

### What the learner sees, in order

1. Their own answer, verbatim, retained on screen.
2. The revealed model answer and the rubric points, **as unticked controls**. The
   learner ticks them. This is the self-assessment path, and it comes first so the
   learner does the retrieval work before seeing any suggestion (Bangert-Drowns et al.
   1991: feedback effects vanish when learners can peek before attempting).
3. Only then, and only behind an explicit disclosure, the model's per-point suggestion.

**Default: `suggestion_reveal = after-self-mark`.** Settings ship all three values
(`on-request`, `after-self-mark`, `never`) per Directive §3, because pre-filling is
defensible for a tired learner reviewing forty EMT items and anchoring is a real cost
for a learner trying to learn.

### Copy and typographic rules

- A suggestion never renders a number, a percentage, a fraction, a check glyph, or a
  cross glyph. It renders as text next to an unticked control. `UI-SPEC.md` §semantic
  tokens already gives `--pending` as distinct from `--ok`/`--bad`; use it and never
  the other two.
- Plain chrome inside a labeled container, per `UI-SPEC.md` LOCKED rule that a model
  acquires no typographic voice of its own (Phase 8 SC6).
- The existing copy string is right and should be reused verbatim: *"A review is
  pending. This attempt counts as work, not as mastery yet."* (`UI-SPEC.md:344`).

### The accept action

The accept **is** `evidence.mark_event(..., marker="human")`. It already exists, it is
already append-only, it already carries `rubric` as N booleans, and it already refuses a
non-human marker. Phase 8 adds a *different* event type, `mark_proposal`, which
`marks_by_event()` does not consider — so a proposal cannot change `review_state` by
existing. Concretely: **do not relax the `marker != "human"` guard in `mark_event`.**
Phase 8's TEACH-09 should add an event type, not widen a check. A widened check is one
config flag away from being the thing §4.1 forbids.

Batch accept over one screen of N suggestions is the correct ergonomic concession, and
it is the real need behind any auto-accept request: same human authority, one gesture.

### A suggestion never accepted

Nothing happens, forever, and that is the designed outcome. The proposal stays in the
log as the fact that a suggestion was made. The response's `score` stays `None`. The
`review_state` stays `pending`. `report` already counts and lists pending shorts
(`evidence.py:1175`, `1248`) and will list this one indefinitely. No expiry, no
timeout-to-accepted, no decay into a grade.

### May a pending mark influence selection or scheduling before acceptance?

**No — but "no" does not mean "invisible."** A pending response is a third state for
Phases 7 and 10, not a zero:

- It **counts as an attempt** and suppresses immediate re-asking, because the learner
  did the work and re-serving it in the same session is a bug.
- It **grants no mastery credit** and contributes to no correctness ratio. The existing
  counters already do this correctly (`evidence.py:668-676` buckets `pending`
  separately from `correct`/`wrong`; `runtime.py:206-215` the same).
- It **never advances a retention interval.** An interval extension on unverified work
  is a silent auto-accept with a scheduler's face on it.
- Phase 10 must render `unknown`, not a low score, for an objective whose evidence is
  mostly pending. `UI-SPEC.md` scenario 9 already requires exactly this posture.

---

## R4.6 — Adaptability

None of the four requires an edit to `score_response()`.

**(a) `sympy` replaces the hand-rolled Math checker.** A second registration under the
same accept rule: `NORMALIZERS["math"]` selected by config key
`math.equivalence_strategy = sample | sympy`. Phase 9 SC8 already states the right
principle ("the rule, not the library, is the contract"); this only names the seam.
Ship both (Directive §3): the stdlib sampler is the offline floor, sympy is the exact
path where a dependency earns it. Extensibility Rule 6 requires the seam be proven by a
stub, so the test registers a throwaway third strategy. **Cost:** one module, one config
key, one dependency (optional, import-guarded), strategy name already going into the
event under Rule 4.

**(b) A local 7900 XTX model replaces a hosted one for tier 3.** Zero scorer
involvement of any kind. This is Phase 8 SC2 and SC7, already specified as a one-line
config change with a new adapter module. **The fact that this question has nothing to do
with the scorer is the proof that putting tier 3 outside it was right.** Evidence from
R4.4: expect roughly 0.02 to 0.05 κ loss on judging, more on open-ended rubrics, and an
unmeasured quantization risk. None of that matters to correctness here, because the
output was never accepted evidence in either case. That is the whole benefit of the
design in one sentence. **Cost:** zero, in this scope.

**(c) A new item type needs a checker nobody has written.** The registry lookup misses,
`canonical_key` returns `None`, `score_response` returns `None`, and the item is
permanently pending and permanently human-markable. **The system degrades to "a human
marks it," never to a crash and never to a false verdict.** That is the correct default
and it costs zero code, because it is the same path `short` already takes. Add
`item.no_normalizer` as a lint **warning** (not error) so the author learns at lint time
that this type will land in the review queue. **Cost:** one lint code.

**(d) A tier-3 strategy becomes reliable enough to auto-accept: config change, and
should it be possible?**

**It must be impossible. Not off-by-default, not gated behind a warning: absent.** Four
independent reasons, any one sufficient:

1. `PLANNING-DIRECTIVES.md` §4.1. A configurable §4.1 is not a non-negotiable.
2. **No threshold exists that would make it safe.** The reliability being waited for is
   agreement, and agreement is not reproducibility. Borderline items are
   non-reproducible across reruns even at temperature 0 (arXiv:2606.26185). A strategy
   cannot become reproducible by getting more accurate.
3. **There is no valid gate variable.** The natural knob is model confidence, and LLM
   confidence is uncalibrated (ECE commonly 0.05 to 0.20; a model saying 90% is right
   70 to 85% of the time). A threshold on an uncalibrated number is a decoration.
4. Ofqual, 14 January 2026, on AI as the sole mechanism for determining a mark.

The concession that *is* right: batch accept (R4.5), plus ordering the review queue by
model-flagged difficulty so the human's attention goes where it matters. That serves the
real need behind (d) without moving the authority.

**Mechanical guard:** the `marker != "human"` `ValueError` in `mark_event`
(`evidence.py:1058`) is the enforcement point, and it must survive Phase 8 unchanged.
Add `T-R4-02` asserting it still raises. If a future phase needs to relax it, that test
turns the relaxation into a visible decision instead of a diff.

---

## R4.7 — Partial credit and confidence weighting

### Verdict

**No fractional score, ever. Yes to N booleans, because they already exist and no door
needs opening.** Decompose to `[{"point": str, "pass": bool}]` — the exact shape
`mark_event` already accepts. The roll-up `verdict` stays a separate dichotomous bool.
Nothing about this is one-way, because Phase 1 already went through the door in the
right direction.

### Costing the alternative

Storing `score: float` on the response event costs:

- **Every existing consumer.** The codebase distinguishes `True` / `False` / `None` by
  identity in at least four places (`evidence.py:672-676`, `evidence.py:1173`,
  `runtime.py:205-215`, `evidence.py:1301-1305`). A float makes it four shapes, forever,
  in an append-only log where old events keep the old shape.
- **Irreversibility.** Append-only means a fractional score written once is in the
  history permanently and every future reader must handle it.
- **Accuracy where accuracy is worst.** The mid-range degradation finding
  (arXiv:2605.07647) says models are least reliable precisely in the partial-credit
  band. Partial credit would import the model's weakest region into the evidence store
  as a number.
- **The domain rule.** NREMT gives no credit for a partially correct response.
  `GRADING.md:112` and `itembank.py:27-29` already say so, and `GRADING.md` already
  scopes `PARTIAL` as describing an answer, never awarding half a mark.

Storing N booleans costs: nothing. It is the current schema.

### Confidence-weighted verdicts

**No.** Uncalibrated (see R4.6 d.3), and a number in a log invites arithmetic on it that
no one intended. If a model proposal carries a confidence, it is stored on the
`mark_proposal` event only, never on the response and never on the mark; it is never
rendered to the learner as a number; and it never enters selection or scheduling. Its
one legitimate use is ordering the human's review queue.

### Derived fractions are fine

"4 of 5 rubric points accepted" computed at read time from the booleans is a legitimate
report view under Extensibility Rule 5 (derived, never stored). It is not a score, it is
not stored, and it is not scheduler input. The distinction between a derived view and a
stored fact is the whole difference between a useful report and a one-way door.

---

## Open rulings and what could not be determined

1. **No within-task A/B of decomposed versus holistic rubric grading exists in
   educational assessment.** The recommendation to decompose therefore rests on accept
   ergonomics, which is solid, and not on accuracy, which is unproven. Do not let a
   plan or a doc restate it as an accuracy claim.
2. **No study measures quantization against judge agreement.** Relevant to Phase 8's
   local backend and unanswerable today. Immaterial to correctness here, since tier 3
   is never accepted; material only to how much of the human's time a bad local judge
   wastes.
3. **Phase 6.1's private tolerance policy needs a version in the evidence event.** Not
   a conflict with SC3, but it is a change SC5's evidence list does not currently name.
   Flagged for `/gsd-discuss-phase 6.1`.
4. **Phase 5's timeout-returns-None** changes SC2's "dichotomous verdict" wording to
   "dichotomous verdict or a recorded non-verdict." That is an additive change to an
   unwritten plan, not a re-spec.
5. **Provenance:** several 2026 figures come from unreviewed arXiv preprints citing
   model names not independently verified. The direction of every finding used here is
   corroborated by at least two sources; individual numbers are not load-bearing.
