# Rule audit (2026-08-15)

## Audit basis and verdict

Audit base: commit `92f2f209cb401365641bd2de0b3aa15fb7fb3b9b` plus the
working-tree rule clarifications present on 2026-08-15 after IL-20260815-05
and IL-20260815-06 were applied. The audit covers the binding sections named in
`RULE-AUDIT-PLAN-2026-08-15.md`, not historical implementation descriptions in
CLAUDE.md. Mirrored statements are one rule family with multiple locators.

The product invariants earn their cost. One assessment authority, one parser,
one scorer, one evidence store, truthful evidence, explicit rights, accessible
equivalence, atomic mutation, and recoverable accepted state protect real
failure boundaries. The demonstrated drag came from two sources:

1. Retired preferences, especially stdlib-only and no-build-step, continued to
   act as vetoes after the 2026-08-09 relaxation.
2. Process controls use high-stakes language for low-stakes ideas and planning
   work. The repository now clarifies that disposition upkeep scales with
   stakes, but the workflow still lacks an explicit lightweight record shape.

The seven IL-20260815-06 clarifications resolve the observed or credible
product-rule ambiguities. This full sweep found no additional product-rule
change with enough evidence to justify amendment. The replanning gate fires
for process tiering and for already reopened source-intake work. The proposed
delta is in `RULE-AUDIT-ROADMAP-DELTA-2026-08-15.md`; ROADMAP.md is unchanged.

## Rule inventory

The table normalizes 34 distinct binding rule families. `Keep` means the rule
is clear enough after current dated notes. `Clarified` means the 2026-08-15
additive note remains necessary. Locators identify the canonical or most useful
mirror; AGENTS.md, CLAUDE.md, SOURCE-TO-COURSE.md, AGENT-WORKFLOW.md,
PLANNING-DIRECTIVES.md, synthesis sections 2, 6, 10 to 12, and UI-SPEC.md
sections 8, 9, and 11 were cross-checked.

| ID | Normalized rule and intent | Class | Locators | Misreading or blocking evidence | Strength | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| RA-001 | One parser and one scoring authority; extend the authority additively, never create a competing verdict. | Product invariant | AGENTS.md rules 1 to 2; CLAUDE.md Runtime invariant; Directives 4.1 to 4.2 | Roughly ten historical cites, mostly sound; IL-05 found wording could freeze capability growth. | Observed ambiguity | Clarified |
| RA-002 | Prose remains pending until a settled review; labeled advisory assessment is allowed. | Product invariant | AGENTS.md rule 3; CLAUDE.md Runtime invariant | No past rejection, but literal wording could block formative AI feedback. | Credible accepted-feature conflict | Clarified |
| RA-003 | Real banks stay out of the repository. | Product invariant | AGENTS.md rule 4; CLAUDE.md Data | No conflicting wanted feature. | No ambiguity found | Keep |
| RA-004 | Evidence and banks are learner-controlled local records; telemetry and vendor-held gradebooks are forbidden, learner export and sync are rights-gated. | Product invariant | AGENTS.md rule 5; CLAUDE.md Data residency; Directives 4.3 | Five historical cites were substantially sound; literal wording could block learner-owned backup or sync. | Observed ambiguity | Clarified |
| RA-005 | Select treatment per objective instead of generating every artifact. | Product contract | AGENTS.md rule 6; SOURCE-TO-COURSE treatment sections | Supports the sound supersession of one-shot generation. | Direct support | Keep |
| RA-006 | Agents may do approved useful work, with citations, uncertainty, bounded authority, review, and recovery. | Product contract | AGENTS.md rule 7; synthesis section 10 | Prevents both agent prohibition and unbounded autonomy. | Direct support | Keep |
| RA-007 | Standardized-test claims require a sourced, versioned blueprint and faithful mappings. | Quality gate | AGENTS.md rule 8; SOURCE-TO-COURSE scope boundaries | No conflicting wanted feature. | No ambiguity found | Keep |
| RA-008 | Inventory approved roots and reuse adequate artifacts before creating replacements. | Process control | AGENTS.md rules 9 to 10; AGENT-WORKFLOW sections 6 to 7 | No feature rejection; prevents duplicate and destructive work. | Direct support | Keep |
| RA-009 | Link, import, copy, move, edit, supersede, migrate, and sync are distinct operations with explicit identity effects. | Product invariant | AGENTS.md rules 10 and 15; synthesis section 6 | Supports conflict-safe file work. | Direct support | Keep |
| RA-010 | Authored lessons remain useful in portable static form; rich interactions provide accessible operation and a study-usable fallback. | Product contract | AGENTS.md rule 11; SOURCE-TO-COURSE learner experience | Literal equivalence wording could ban simulations and manipulatives. | Credible accepted-feature conflict | Clarified |
| RA-011 | Audit legacy artifacts before bounded, value-adding upgrades; preserve identity and assessment semantics. | Process control | AGENTS.md rule 12; AGENT-WORKFLOW section 7 | No conflicting wanted feature. | Direct support | Keep |
| RA-012 | Preserve user quotations separately and route meaningful product direction through the vision funnel. | Process control | AGENTS.md rule 13; AGENT-WORKFLOW sections 2 and 10 | High value for consequential direction, but expensive if applied to incidental task mechanics. Current workflow already limits promotion by meaning and stakes. | Plausible process overreach | Keep, tier proposed |
| RA-013 | Preserve viable breadth; reject only on a named quality conflict; keep rejection history and allow archival with pointers. | Process control | AGENTS.md rule 14; CLAUDE.md Preserve breadth; Directives 3a | Prevents silent idea loss; upkeep can become noisy without a low-stakes tier. | Observed process cost | Clarified, tier proposed |
| RA-014 | Every consequential operation names object, owner, authority, rights, source of truth, state, validation, and recovery. | Product/process control | AGENTS.md rule 15; synthesis sections 2, 6, 10 | High value for durable writes; excessive for read-only or trivial work if read literally. | Plausible process overreach | Keep, tier proposed |
| RA-015 | Discovery is read-only and scoped; finding a file grants neither mutation nor egress. | Safety rule | AGENTS.md workflow; AGENT-WORKFLOW section 7 | No conflicting wanted feature. | Direct support | Keep |
| RA-016 | Durable mutations use expected-base comparison, temporary validation, atomic commit, journal, and recoverable prior state. | Product invariant | AGENTS.md object summary; synthesis section 6 | No conflicting wanted feature; prevents mixed state and silent overwrite. | Direct support | Keep |
| RA-017 | Rights are separate grants for read, quote, transform, remote process, package, export, and share; unknown stays restrictive. | Product invariant | AGENTS.md object summary; synthesis sections 6 and 11 | No conflicting wanted feature. | Direct support | Keep |
| RA-018 | Accepted, pending, confidence, validation, rights, availability, staleness, and conflict are separate axes. | Product invariant | AGENTS.md object summary; synthesis sections 2.3 and 4.1 | Supports sound rejection of aggregate mastery. | Direct support | Keep |
| RA-019 | Learner notes and artifacts never silently become source truth, keys, scores, or mastery. | Product invariant | AGENTS.md workflow; synthesis sections 7.2 and 12.4 | Sound rejection retained. | Direct support | Keep |
| RA-020 | Derived views, indexes, HTML, and caches are disposable and never the sole canonical meaning. | Product invariant | AGENTS.md object summary; synthesis sections 2.2 and 12.4 | Sound rejection retained. | Direct support | Keep |
| RA-021 | Representative authored outputs receive human accessibility review; agents do not self-certify. | Quality gate | AGENTS.md and CLAUDE.md accessibility summaries; synthesis 11.4 | Undefined representative sampling could require review of every artifact. | Credible throughput conflict | Clarified |
| RA-022 | Export or package promises require a clean-machine offline restore that reports loss. | Quality gate | AGENTS.md clean recovery; synthesis loops G and section 6 | No conflicting wanted feature. | Direct support | Keep |
| RA-023 | Core learning degrades without network; model-only actions become explicitly unavailable. | Product contract | CLAUDE.md Network; UI-SPEC 8 | No conflicting wanted feature; this is resilience, not a general network ban. | Current wording clear | Keep |
| RA-024 | Runtime capabilities have daemon and CLI clients; presentation behavior needs an accessible equivalent, not a CLI duplicate. | Architecture rule | CLAUDE.md Surfaces | Literal wording doubled presentation work. | Credible accepted-feature conflict | Clarified |
| RA-025 | Format evolution preserves existing banks, while documented deprecation and explicit migration may retire elements. | Compatibility rule | CLAUDE.md Compatibility; Directives 4.4 | Literal additive-only wording could make mistakes permanent. | Credible maintenance conflict | Clarified |
| RA-026 | Dependencies, bundlers, and non-Python components are allowed on merit; historical stdlib-only text is preference, not veto. | Preference boundary | CLAUDE.md Constraints; Directives 4a | About twenty historical blocks, including eleven cargo-culted cites. | Direct observed harm | Keep and enforce |
| RA-027 | Third-party artifacts require pinned versions, checksums, license review, and an explicit maintenance policy. | Safety rule | Directives 4a Supply chain | Zero-dependency had incorrectly stood in for this control. | Direct observed omission | Keep; IL-09 registered |
| RA-028 | Authored arbitrary script and untrusted active content cannot acquire runtime authority; trusted registered interactions remain possible. | Safety rule | Directives 4a; synthesis 7.4 and 12.4; UI-SPEC 9 and 13 | One accessibility cite was miscited, but the safety and VIS-01 grounds stand. | Direct support | Keep |
| RA-029 | Accessibility requires semantic controls, keyboard completion, equivalent nonvisual tasks, visible labels, focus, status, reflow, contrast, and honest degradation. | Quality gate | UI-SPEC 8 items 1 to 9 | Six historical cites, substantively sound. | Direct support | Keep |
| RA-030 | Runtime-gated feedback never leaks keys, hidden tiers, or delayed diagnostic/exam correctness through DOM or accessibility text. | Product invariant | UI-SPEC sections 5, 8, and 9 | Five authority cites were sound. | Direct support | Keep |
| RA-031 | Agent authoring progresses from report to explicit bounded approval; autonomy does not bypass citations, validation, diff, or audit. | Safety/process control | UI-SPEC section 5D; synthesis section 10 | No conflicting wanted feature. | Direct support | Keep |
| RA-032 | Parallel research is bounded to independent questions, produces named artifacts, and synthesis begins after coverage checks. | Process control | AGENT-WORKFLOW section 4 | Useful for consequential research, excessive for a small inline inquiry if generalized. | Plausible process overreach | Keep, tier proposed |
| RA-033 | Accepted recommendations name owner, evidence, dependency, verification, failure, degraded state, migration, docs, and maintenance; irreversible contracts require prototypes. | Process/quality gate | AGENT-WORKFLOW section 8; Directives 3a | Earns cost for durable commitments, but is too heavy for reversible low-stakes recommendations. | Observed process cost | Keep, tier proposed |
| RA-034 | Repository prose avoids em dash characters except verbatim source quotations and additive user statements. | Style rule | AGENTS.md and CLAUDE.md Prose style | No feature conflict; mechanical lint is preferable to repeated manual policing. | No ambiguity found | Keep |

### Source line map

Line spans below define the audited revision's binding regions. Individual
table locators resolve within these spans; mirrored prose outside them is
descriptive or historical and was not counted as another rule.

| Source | Audited line spans |
| --- | --- |
| `AGENTS.md` | rules 1 to 15 at 52 to 134; object and authority summary at 136 to 197; course workflow at 199 to 240; prose style at 242 to 247 |
| `.claude/CLAUDE.md` | course workflow at 42 to 78; prose style at 80 to 86; direction rules at 88 to 106; object and authority summary at 108 to 176; runtime invariant at 178 to 194; constraints at 196 to 235 |
| `.planning/SOURCE-TO-COURSE.md` | course-building loop at 34 to 87; quality contract at 88 to 177; agent workspace at 178 to 207; scope boundaries at 208 to 222 |
| `.planning/AGENT-WORKFLOW.md` | authority at 10 to 32; capture at 33 to 52; research at 71 to 90; dispositions at 91 to 112; authority check at 113 to 134; file operations at 135 to 151; execution at 152 to 166; handoff at 167 to 182; drift audit at 183 to end |
| `.planning/PLANNING-DIRECTIVES.md` | autonomy at 88 to 104; conflict at 105 to 129; dispositions at 130 to 169; invariants at 170 to 186; constraint basis at 187 to 246; execution split at 247 to 286; ideaboarding at 298 to 317; vision routing at 377 to end |
| `.planning/research/phase-16/14-synthesis.md` | product model at 136 to 194; file model at 350 to 391; agents at 533 to 574; cross-cutting rules at 575 to 603; portfolio and ledgers at 604 to 705 |
| `.planning/UI-SPEC.md` | accessibility at 580 to 602; agent boundaries at 603 to 616; verification gates at 634 to 656; do-not-build gates at 666 to 677 |

## Retrospective feature audit

### Population and reconciliation

The seed sweep in `research/2026-08-15-rejection-rule-tally.md` searched all
disposition records under `.planning/`. This audit treats the following as the
reconciled population:

- 14 permanent rejection or supersession rows in synthesis section 12.4.
- 10 backburner rows in synthesis section 12.5.
- 20 constraint-audit findings summarized in the seed sweep.
- 7 disclosed cost or preference dispositions outside the permanent ledger:
  inline hint stack H3, guided tour F3, custom titlebar, margin sidenote R3,
  data-URL fonts, TanStack Table, and cookbook style.

Repeated roadmap, DECISIONS, vision inbox, and research-brief mentions are
cross-references, not new proposals. The seed sweep's approximate counts cannot
support a more precise repository-wide denominator, so the audit reports 51
normalized candidates in these four evidence sets and does not convert prose
mentions into extra rows. No candidate was unclassifiable.

### Classification

| Set | Count | Result under clarified rules |
| --- | ---: | --- |
| Synthesis 12.4 | 14 | All stand. Three are supersessions that preserve the user value; eleven are hard rejections grounded in truthful evidence, learner agency, safety, accessibility, rights, authority, provenance, portability, or recovery. None depends on stdlib-only. |
| Synthesis 12.5 | 10 | All remain viable backburner items with dependencies and revisit triggers. They are not rejections and need no reopening. |
| Constraint audit | 20 | The stale preference caused the demonstrated error cluster. Existing IL-07 through IL-11 reopen or route the actionable cases. F7 and F10 remain revisit-marked until a phase has a concrete need. Other cases either reversed already or survive on a valid merit ground. |
| Cost/preference dispositions | 7 | These are disclosed design choices, not rule-based hard rejections. Keep them as reversible local decisions. Promote any to backburner when its user value remains live and a concrete revisit trigger exists. |

Already reopened, with no duplicate entries created in this pass:

- IL-20260815-07, PDF and DOCX source intake.
- IL-20260815-08, pytest or test-runner adoption.
- IL-20260815-09, real supply-chain policy.
- IL-20260815-10, non-stdlib Anki import.
- IL-20260815-11, packaging conflict for Phase 18.

No synthesis 12.4 rejection weakens under the clarified rules. The inaccessible
implementation of an interactive feature remains rejected, while the
interactive capability itself remains allowed through RA-010 and RA-029.

## Friction verdict

Reliable wall-clock measurements do not exist in repository history. The
observable evidence is citation frequency, repeated artifacts and fields, and
documented reversals or stalls.

Product-rule cost is justified. The one-authority and truthful-evidence rules
account for many rejection citations, but almost all of those decisions still
stand. Accessibility, rights, local evidence, atomic mutation, and recovery
rules also map directly to named failure modes.

The measured rule failure is stale-authority drift. A relaxed preference still
performed roughly twenty vetoes, triggered follow-up research, and left at
least five decisions needing reopening or reconciliation. The repair is not a
weaker architecture rule. It is stronger authority labeling and a requirement
to quote the currently binding text before rejecting.

Process cost is real but only partly measured. Consequential work currently
asks for disposition, origin, evidence, exact reason, conflicting rule,
alternative, date, reconsideration condition, owner, dependency, validation,
failure, degradation, migration, documentation, and maintenance. Those fields
are valuable for schemas, accepted product direction, durable writes, and hard
rejections. Requiring the full set for a reversible low-stakes idea creates
recording duplication without equivalent recovery value.

Recommended tier:

- Trivial or reversible work: one local note or task entry containing intent,
  owner, next action, and undo when mutation occurs.
- Consequential proposals and durable writes: current operation and accepted-
  recommendation fields.
- Binding formats, authority changes, rights or egress changes, hard
  rejections, and roadmap scope: full evidence, prototype, ledger, and user
  decision gates.

This tier is a proposed process clarification, not an authorization to weaken
assessment, accessibility, rights, mutation, or recovery invariants.

## Applied changes and gate result

- Improved `RULE-AUDIT-PLAN-2026-08-15.md` with stable IDs, authority classes,
  deduplication, evidence thresholds, measurable population rules, friction
  proxies, and a mutation gate.
- Verified the seven IL-20260815-06 clarifications are present in AGENTS.md and
  CLAUDE.md. No additional wording change met the evidence threshold.
- Verified IL-07 through IL-11 already preserve the reopened ideas. No duplicate
  IDEA-LEDGER entry was added.
- Fired the replanning gate and wrote a proposal. ROADMAP.md was not edited.
