# Learning treatment prototypes

Owner: Weibao for experience and product acceptance. These are reversible
interaction sketches, not accepted course formats or production features.

Open `index.html` locally. Both pages work offline without a build step.
Each page has an accompanying Markdown source and static fallback.

The first batch interprets the 2026-09-10 prototype request as the newest
figure/table, chapter-tier, and source-wisdom proposals. The request's routing
instructions apply to each subsequent link. The owning ideas are
`IL-20260910-01`, `IL-20260910-02`, and `IL-20260910-03` in
`../../.planning/IDEA-LEDGER.md`. The visual baseline is the accepted
`../course-preparation/` study desk.

## Current direction, 2026-09-11

The user has authorized continued prototype work and deferred the named human
and real-course reviews. Historical sections below retain the checks owed at
the time. This section owns their present disposition and replaces the earlier
stop before another synthetic step.

D1: Reproducing the original figure, source dialog, and placement experience is
allowed as a user choice. Exact reproduction versus adaptation remains a
presentation choice for later review. No source treatment was rejected because
the first hotspot candidate did not contain it.

D2: Drag-and-drop is the current diagram default. A supplied word bank remains
visible during placement. Typed diagram answers and table blanks each offer an
answer-bank toggle. Hiding a bank is a learning-practice choice. Exam-style
practice must preserve the response choices, cognitive demand, and conditions
required by its actual target exam. The complete value bank can make a table
blank solvable by eliminating visible values, so that exercise is labeled
source-value recognition or recall, not comparison reasoning.

D3: Human touch, screen-reader, zoom, and aesthetic review are deferred until
representative hardware and reviewer time are available. Real-course comparison
is deferred until an approved course and source are selected. Durable format
acceptance is deferred until production promotion is proposed. Weibao owns these
reviews. None has passed by deferral, and none blocks this synthetic chain.

Current evidence: the diagram studio supports drag, click, and dropdown
placement with each label used at most once. Word/value-bank choices, source
dialogs, and typed responses retain their state. The existing runtime separately
validates one four-label `dnd` item and one rainfall-comparison `short` item.
The studio remains an ungraded authoring preview. Placement drafts now export
as an existing `dnd` item with selected locations, the full word bank, a proposed
source key, and self-contained source context. Monday comparison now exports a
`short` draft through the separate table treatment described under
[Studio table export](#studio-table-export-2026-09-12). Typed labels and table
retrieval remain preview-only. The placement packet is recorded below under
[Studio placement export](#studio-placement-export-2026-09-11).

Official format evidence and the independent review are in
[EXAM-FIT-REVIEW.md](runtime-candidate/EXAM-FIT-REVIEW.md). Exam orientation and
the user's original words are recorded in
[User Vision](../../.planning/USER-VISION.md#2026-09-11-orient-learning-and-practice-to-the-actual-examination).

## Scope and recovery

The HTML and Markdown here are original synthetic material. Page interaction
state is temporary. An explicit placement or Monday comparison export creates
a separate downloaded bank draft for author review. Reload discards unsaved page changes. Remove this
directory to undo the prototype, with any downloaded copies retained separately.
No production runtime, schemas, learner files,
course graph, source rights, scoring, or evidence store are changed.

Two Terra agents at medium effort own disjoint figure and chapter files.
The coordinator owns the entry page, browser verification, and this packet.
Existing dirty repository changes remain outside this batch.

## First-batch evidence and review disposition

EVIDENCE: The coordinator reviewed both HTML implementations and Markdown
companions. Chromium exercised keyboard label selection and placement, draft
retention across modes, table wording edits, reset, both tier axes, stable
chapter and objective IDs, narrow-screen chapter reachability, reader focus,
and previous/next navigation. All focused checks passed on the final pages.
Exact Markdown anchors, empty browser storage, zero HTTP requests, and zero
script errors passed. All three pages fit 1440 and 390 pixel viewports without
page overflow. Desktop and narrow screenshots were inspected.
Final quick preflight passed every executed gate. Full Python, JavaScript,
and clean-tree checks were skipped by quick mode. `git diff --check` passed.

The repeatable interaction gate is `node prototypes/learning-treatments/verify.mjs`.
It requires an available Playwright installation and Chromium. An external
installation can be selected through `ITEMBANK_PLAYWRIGHT_MODULE`, the module
entry path, and `ITEMBANK_CHROMIUM`, the browser executable path. These are test
dependencies only. The pages have no dependencies.

AUDITS: This section owns the bounded review. Narrow chapter hiding, lost focus
after selection, global character shortcuts, placeholder source paths, and
lost drafts across mode switches were found and repaired. A figure-handler
regression failed the keyboard placement assertion. The coordinator replaced
the overlapping handlers with one script, then verified the focused gate.
These findings are reconciled as fixed within the synthetic prototype scope.

Human touch, screen-reader, text and browser zoom, and aesthetic review remain
pending with Weibao. The real-course comparison, approved source intake,
lintable bank output, and runtime scoring promotion gates remain unimplemented.
No production module audit or learning-effect claim is made. Review these
surfaces before proposing a durable format or adapting real course material.

## Fresh evaluation and second link, 2026-09-11

User direction: "consider the work and see if theres better, and then continue
accoreingly". Evaluate whether authors can shape and try an activity and whether
learners can inspect prerequisite and source context without losing their place.
Earlier passing tests establish mechanics, not usefulness or learning effects.

| Option | Present fitness | Change cost and disposition |
| --- | --- | --- |
| Retain the text-draft demos | Preserves working controls but cannot test the resulting visual activity | Lowest cost. Original observations remain in the first-batch section. |
| Add direct source selection, an ungraded preview, and contextual navigation | Makes the intended task observable without accepting a format | Bounded prototype changes. Selected for this link. |
| Connect arbitrary source intake and production scoring now | Could establish a real authoring pipeline but still lacks a demonstrated valid output shape | Higher authority and format cost. Defer until one synthetic candidate passes existing contracts. |

The official [H5P drag-and-drop tutorial](https://h5p.org/tutorial-drag-and-drop-question),
checked 2026-09-11, separates background material, drop zones, labels, and the
resulting activity. That supports testing the author-to-preview transition.
No H5P assets, implementation, scoring rules, or dependency were adopted.

F1: The original figure page kept all labels visible and edited a disconnected
text draft. It now lets the author select actual labels or table cells, preview
missing values, enter trial responses, and review the exact instruction,
selection, and purpose. Figure placement supports drag, click selection, and
dropdowns. Each source retains its draft. Text and placement responses are
separate. This fixes the interaction gap, not the valid-bank-output gap.

F2: The original depth grouping had no inspectable prerequisite edges. It now
derives depth from explicit synthetic dependencies and provides prerequisite
navigation with rationale. The four chapters happen to retain the same linear
order. The new evidence is the inspectable dependency and repair action, not an
artificially reordered list. Real-course usefulness remains unverified.

F3: Raw Markdown links do not create rendered HTML anchor targets on the local
server, which reports `text/markdown`. Both pages now show source context in a
native dialog. Closing restores focus and keeps the selected source, chapter,
projection, and trial responses. Raw files are secondary links in a new tab.

EVIDENCE: The coordinator inspected the figure implementation and the changed
chapter functions, not the complete production UI. A bounded independent Luna
review challenged the initial task fitness. The chapter owner used Terra at
medium effort. `verify.mjs` covers masking, actual draft-to-preview behavior,
keyboard placement, drag placement, table cell selection, independent draft and
response retention, exact source-dialog return, empty selections, reset, derived
depth groups, prerequisite navigation, stable identities, and source anchors.
No HTTP requests or browser storage were created by file-based verification.
Desktop and narrow screenshots passed overflow checks and were inspected.
Quick preflight passed its executed gates. Full Python, JavaScript, clean-tree,
touch-hardware, screen-reader, zoom, and aesthetic acceptance remain unclaimed.

AUDITS: F1 through F3 are reconciled within prototype scope. Valid bank output,
runtime integration, a real-course comparison, and human acceptance remain
open. The next link below owns the smallest runtime-fit experiment. Weibao owns
human and product acceptance. Prior source material is preserved in the Markdown
companions. No production or pre-existing dirty files were changed.

## Continuation packet: one synthetic runtime-fit candidate

GOAL: Prove one synthetic figure or table treatment can produce a reviewable
item in an existing bank format, with deterministic lint and runtime evidence.

OWNER: Weibao decides experience acceptance and unresolved tier semantics.

SCOPE: New `runtime-candidate/` subdirectory here, its narrow validation script,
and this README for the returned evidence. Read the source companions and
existing format contract. Use the author-bank skill. Pick one existing type
based on the intended construct, not on a desire to invent a new type.

DO NOT TOUCH: Existing dirty files, current prototype UI, production modules,
durable schemas, real course content, real scoring or evidence state, external
services, commits, or pushes. Existing lint and runtime may run on newly created
synthetic files in a disposable temporary root. All test session and evidence
outputs must stay there. Never reimplement or edit the scorer.

CONTEXT: Apply `$daisy-chain-work`, `$efficient-agent-routing`, and
`$evidence-gated-handoff` to each link. Use one balanced owner at medium effort.
Delegate only independent files or a concrete independent verification gate.
Do not interpret synthetic sketches as satisfaction of the real-course
promotion gates in the idea ledger.

NEXT ACTION: Run `python3 itembank.py spec`, inspect only relevant synthetic
fixtures, then map one source treatment into an existing item format. If no
existing format preserves the construct, save that precise incompatibility and
the smallest proposed alternative. Do not change the format in this link.

GATE: One original synthetic candidate lints without errors, cites the exact
source, and has inspectable static meaning. Exercise it through the existing
runtime in an isolated temporary root. Verify the public item obeys disclosure
and that runtime alone determines the result. If prose is selected, pending
review is the required result. Retain all validation limits and draft/key-review
status. No published or accepted assessment is implied. Review the actual diff
and run required preflight. Stop after the bounded gate or a specific format
incompatibility, then reconcile with this owner before another link.

RETURN: Changed paths, checks actually run, observed defects, remaining gates,
and one next action. Preserve exclusions in every successor prompt.

The prior claim that cross-chat creation was unavailable is superseded.
The current host exposes `create_thread` and `list_projects`. Use the same local
checkout because the required prototype inputs are uncommitted. Each successor
must apply both routing skills and preserve this packet's exclusions. Start only
after the current link's gate is verified. Do not infer a running successor from
the existence of this packet.

## Runtime-fit candidate result, 2026-09-11

`runtime-candidate/water-process-hotspot.txt` is one original synthetic draft
that maps the Figure 2 location-selection construct to the existing `visual`
hotspot grammar. It cites `figures.md#source-figure-2` and preserves an
inspectable static description of both source targets. The private scoring
envelope accepts only the lake-arrow target. Its public runtime projection
contains neither `SCORING`, `accepted`, nor the keyed process label. It does
contain both response identifiers, as required for interaction, but not their
private acceptance mapping. The existing runtime, not the validation script,
returned false for the cloud-arrow response and true for the lake-arrow response.

The `.txt` files contain Markdown accepted by the existing parser. The global
Markdown corpus guard does not inspect that suffix, so its pass is not evidence
about these candidates. The explicit candidate validator checks each synthetic
file with the canonical parser and runtime. EVIDENCE:
`python3 itembank.py lint runtime-candidate/water-process-hotspot.txt`
reported zero errors. `python3 runtime-candidate/validate_runtime_candidate.py`
ran both submitted hotspot responses in a fresh system temporary directory and
removed that directory on exit. `python3 scripts/preflight.py --quick` and
`git diff --check` were required after the candidate was added. The final
command results are recorded by the executing link, not inferred here.

LIMITS: This historical candidate establishes parser and scorer compatibility
for selecting a region. It does not settle the diagram's response format.
The later user direction prefers label placement, implemented below, and
keeps source reproduction as a user choice. The item remains draft-only with
`CONFIDENCE: low`. The reviews in Current direction are deferred.

## Placement and table continuation, 2026-09-11

Intent: continue from the historical hotspot into label-to-location matching
and a source-table explanation. Read scope is this prototype, its synthetic
companions, the shipped contract and fixtures, and current official NREMT format
documents. Item text is original synthetic material processed in this hosted
authoring session. Public NREMT documents support format research only. No
official question or key is copied into a candidate. Writes are draft-and-review
prototype edits, with separate additive User Vision updates requested by Weibao.

`runtime-candidate/water-process-placement.txt` preserves four process labels
and their four target locations through the existing `dnd` grammar. The supplied
bank is public response content. Only the runtime knows the private target
mapping. The existing bank renderer uses named destinations. The spatial
diagram remains in the studio, as a separate ungraded preview.

`runtime-candidate/rainfall-comparison.txt` preserves the earlier proposal to
explain Monday's equal-duration observations. It uses `short`, includes 12 mm,
18 mm, the common 24-hour interval and the exact source locator in the public
stem, and leaves every submitted explanation pending. This is learning practice,
not a format listed for the current EMT certification exam. The studio's blank
and optional value bank remain a distinct retrieval treatment.

Both new candidates have zero lint errors and two intentional warnings: no
accepted item ID and low confidence pending review. Statistics and coverage
report one application item and one synthetic objective per file. No exam
distribution or learner-performance estimate is inferred from these samples.

EVIDENCE: `python3 prototypes/learning-treatments/runtime-candidate/validate_runtime_candidate.py`
copies all three banks and their synthetic source into a fresh temporary root.
It runs lint, statistics, coverage, rich HTML builds, and runtime sessions there.
Hotspot and label placement return false for incorrect responses and true for
correct responses. Three varied table explanations each return `score: null`,
`defer_feedback`, and `pending_manual: 1`. Public items withhold keys, rubric,
model text, and accepted mappings. All temporary output is removed on exit.

`verify.mjs` passes the updated default, optional-bank behavior, retained draft
and response state, one-use label movement, drag and keyboard placement, source
return, empty selection, reset, existing chapter checks, exact source anchors,
no network or storage, and desktop/narrow overflow checks. Screenshots were
inspected as a mechanical review, with human review deferred as recorded above.

Final quick preflight passed every executed gate. Full Python, full JavaScript,
and clean-tree checks were skipped by quick mode. The focused JavaScript browser
gate above was run separately. `git diff --check` passed. The bounded User
Vision audit found all three new entries and their exact downstream links.
Its pre-existing reference backlog is unchanged and recorded under IL-20260910-01.

AUDITS: The earlier local evidence-directory mistake remains reconciled by
copying bank and source before running sessions. The newer disclosure test was
corrected to distinguish the runtime's boolean receipt field `accepted` from a
private accepted-state mapping. No runtime code changed. The complete table
bank's elimination shortcut is now visible in the help and static companion.
The independent [exam-fit review](runtime-candidate/EXAM-FIT-REVIEW.md) is
reconciled. Its table-elimination finding is addressed. Its named-destination,
historical-hotspot, and deferred-review limits are retained. No required fix
remains. Two Astra agents at user-requested high reasoning handled this review
and the disjoint User Vision update while the coordinator implemented and tested.

Recovery: remove the two new candidate files and reverse only this link's
prototype hunks to restore the earlier studio. Runtime outputs are disposable.
No accepted course artifact or learner record became stale. Future automatic
export must regenerate previews when source selection or bank settings change.

NEXT ACTION at the close of this earlier link: connect one studio placement draft to a reviewable existing `dnd`
bank export, retaining exact selection, option bank, source locator, and draft
status. Run the same isolated lint/runtime gate on that exported artifact.
Continue with the current routing and handoff skills, and keep production
promotion and the named deferred checks separate from this prototype step.

## Studio placement export, 2026-09-11

GOAL: turn one current studio placement draft into a reviewable existing `dnd`
bank and validate the actual downloaded artifact through the shipped runtime.

OWNER: Weibao owns treatment and later acceptance. The coordinator owns UI
integration and this result. Two Astra agents at user-requested high reasoning
own the pure serializer and the independent export gate in disjoint files.

SCOPE: `placement-export.js`, the figure studio's HTML, JavaScript and CSS,
its static companion, `runtime-candidate/verify_export.mjs`, and this README.
DO NOT TOUCH: production modules, schemas, actual course or learner data,
accepted banks, existing evidence, commits, pushes, and external service writes.
The hosted authoring session uses only the already approved synthetic source.
All generated test banks, HTML, downloads, sessions, and evidence use an
isolated disposable root.

CONTEXT: the author chooses locations and wording, then opens Review draft,
Create bank draft, and Download bank draft. All four source labels stay in the
word bank. Only selected locations become targets. Unselected labels map to
an explicit Not used destination. The export does not inherit trial answers.
Each download includes the original synthetic source specimen, exact locator,
static meaning, and JSON-encoded original author wording. The one-line question
joins ordinary whitespace with a visible notice. Unsafe structural instruction
text is refused visibly. The artifact remains an unaccepted, low-confidence
draft containing a proposed key. The browser does not claim to have run lint.

GATE: all 15 nonempty source selections produce exactly one `dnd` item without
lint errors. The public item preserves the full option bank and exact selected
destinations while withholding private mappings. Correct and incorrect
responses pass through the runtime. Author-text and trial-answer isolation
checks pass. The browser's downloaded bytes match the reviewed text and pass
the same runtime gate. Existing prototype checks and required quick preflight
also pass before this link is reported complete.

Recovery: close the review to leave the studio state intact. Reopening review
regenerates the bank from current choices and clears old export state. Remove
an unwanted downloaded draft to discard it. Reverse only this link's prototype
hunks and new files to restore the previous studio. No accepted object became
stale. Source, selection, or wording changes require a new draft and validation.

AUDITS: the prior exam-fit review remains reconciled. Source reproduction stays
a user choice, and the named human and real-course checks remain deferred.
This exporter changes no exam-format policy or production format acceptance.

EVIDENCE: the coordinator inspected the serializer, UI integration, and complete
independent export gate. The final full `runtime-candidate/verify_export.mjs`
run exited zero. All 15 nonempty selections passed canonical lint, parsing,
session start, and key-free public-item checks. Partial and full selections
passed statistics, offline build, and runtime correct/incorrect submissions.
The browser downloaded at 390 pixels wide. Its actual saved file matched the
reviewed bytes, passed canonical lint, and returned true for the correct mapping
and false for a swapped mapping. A wrong trial response did not enter the key.

Exact instruction, purpose, and selected-label metadata roundtripped through
JSON. Ten hostile-text cases produced six safe single-item exports and four
explicit refusals. Unsupported formats and invalid selections were refused.
The browser displayed the refusal and cleared the prior export. No network
request or browser error occurred. All generated banks, builds, sessions,
downloads, and evidence were removed from their exact temporary root. Desktop
and narrow screenshots received mechanical inspection only.

The existing `verify.mjs` interaction gate passed separately. Final
`python3 scripts/preflight.py --quick` passed every executed gate. Full Python,
full JavaScript, and clean-tree checks were skipped by quick mode. The two
focused browser gates were run separately. `git diff --check` passed. No
production module was changed or comprehensively reviewed. The verifier used
the canonical parser and scorer rather than implementing either again.

Reconciled finding: the independent verifier caught malformed JSON for the
selected-label array. The serializer owner corrected array encoding. The final
gate parses and checks this metadata for every selection. No required export
fix remains. This link used the requested daisy-chain and efficient-routing
skills to keep one bounded unit, two disjoint Astra high-reasoning lanes, and
independent acceptance evidence.

NEXT ACTION: the requested synthetic placement-export unit is complete. The
author can use Review draft, Create bank draft, and Download bank draft. No
successor task is started solely to extend this chain. Typed/table export,
arbitrary-source authoring, and production integration remain outside this unit
until selected as a new bounded outcome. The deferred reviews retain their
owners and revisit conditions in Current direction.

RETURN: report the working export path, the passing focused and quick gates,
the prototype-only status, and the outstanding deferred reviews. No commit,
push, accepted course revision, or learner-record change was made.


## Studio table export, 2026-09-12

GOAL: A5 now exports one synthetic Monday comparison as an existing `short`
item through Review draft, Create bank draft, and Download bank draft.
The missing studio-to-bank path is implemented. It retains the earlier
retrieval exercise as a separate treatment, including its elimination caveat.
The comparison keeps both values visible and asks for one prose explanation.

OWNER AND SCOPE: A5 owns the figure studio changes and focused table export
verification. Weibao owns human and product acceptance. The coordinating task
and A1 receive this evidence for later integration. The starting revision was
`e7c242a89d16ecd2d715a0cb6b7197ab285bbff6`, with clean prototype files and other
lanes already dirty. No Git mutation was performed. Only original synthetic
source text was processed in this hosted authoring session. No third-party
source, real learner record, external service, or accepted course was changed.

CHANGED PATHS: `figures.html`, `figures.js`, `figures.css`, `figures.md`,
`table-export.js`, `runtime-candidate/verify_table_export.mjs`, and this README.
`placement-export.js`, chapter files, production code, schemas, and scoring
policy are unchanged by A5. Other concurrent code edits are outside this lane.

F5: Resolved in the synthetic lane. The downloaded file embeds Monday,
Gauge A = 12 mm, Gauge B = 18 mm, equal 24-hour intervals, and
`figures.md#source-table-1`, Table 1, Monday row. Its public stem preserves
that context without needing a source file beside the download. The fixed
model answer and rubric come from the existing reviewed candidate. Exact
current author wording is preserved in the stem and JSON author metadata.
Author purpose remains an author note, not scoring authority. Prose trial
responses never enter exported key material. Structural text in either author
field is visibly refused. This bounded serializer accepts one plain-text line
per field and one fixed Monday comparison, not arbitrary table authoring.

F6: Resolved in the synthetic lane. Source, treatment, selection, wording,
bank-setting, reset, and view changes clear the old export. Each review rebuilds
its draft from current state. Retrieval and comparison retain independent
wording and trial responses. Source inspection returns focus and preserves the
comparison response. No preview response is evaluated or persisted.

EVIDENCE: `node prototypes/learning-treatments/runtime-candidate/verify_table_export.mjs`
passed actual browser download byte equality against the displayed bank draft,
canonical CLI lint (one item, zero errors, two intentional warnings for missing
accepted ID and low confidence), stats (one application `short`), coverage
(one synthetic comparison objective), and a rich HTML build. Three distinct
prose responses each returned `score: null`, `defer_feedback`, and
`pending_manual: 1`. Public items and submission receipts withheld model and
rubric fields. Browser checks passed exact source return and focus, retained
separate drafts, stale export clearing, ten visible structural-text refusals,
390-pixel studio and review overflow checks, and no remote requests or script
errors. All banks, builds, downloads, sessions, and evidence used a separate
system temporary root and were removed on exit.

The unchanged placement gate `runtime-candidate/verify_export.mjs` passed all
15 selections, exact metadata, lint, disclosure and correct/incorrect runtime
results, hostile-text handling, and actual download equality. The unchanged
`verify.mjs` passed existing figure and chapter interactions, source anchors,
no storage or network, and desktop/narrow layouts. Browser tests use the
README's existing Playwright and Chromium environment overrides.

`python3 scripts/preflight.py --quick` passed every executed gate. Full Python,
full JavaScript, and clean-tree checks were skipped by quick mode. The focused
browser gates above ran separately. `git diff --check` passed. No concurrent
or pre-existing failure appeared in these executed gates. Full integrated
validation belongs to A4 after the code lanes stop.

REVIEW AND LIMITS: A5 inspected its actual diff and the complete new exporter
and verifier. Production parser and scorer implementations were not audited.
The tests call their canonical CLI. The prior EXAM-FIT-REVIEW F1 elimination
finding remains addressed by separate treatment labels. F2 through F4 retain
their prior limitations. This is a synthetic compatibility and interaction
pass, not whole-exam fidelity, learning efficacy, independent review, or human
accessibility acceptance. Human touch, screen-reader, zoom/reflow, visual,
real-course, and durable-format acceptance remain deferred with Weibao under
the existing direction. Arbitrary edits can diverge from the fixed comparison
rubric, so the whole item still requires human review before accepted use.

RECOVERY: reverse only A5's listed prototype hunks and remove its two new
files to restore the prior studio. Reload discards temporary studio state.
Delete separately downloaded drafts independently. No accepted data became
stale. Do not reset the shared checkout or discard concurrent lane edits.

NEXT ACTION: A1 reviews the returned artifact and exact diff after code lanes
stop, then alone launches the bounded A4 integration successor. A5 creates no
overlapping successor.
