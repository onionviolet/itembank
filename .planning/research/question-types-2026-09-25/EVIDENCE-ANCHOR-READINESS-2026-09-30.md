# Fixed evidence anchors: executable readiness, September 30

Status: prototype proved; the exact production declaration below is ready for
direct user review. No production format acceptance is inferred. This report
owns P3's bounded readiness result, not current STATE or all of F3/T-ANCHOR.

## Scope and reused authority

A2 P3 requested stable predefined spans tied to source revision, offsets, quote
and passage fingerprint. AUDIT-REMAINING F3 retains accepted declaration,
lint/public projection and stale selection recovery as production gates.

Inventoried and reused `prototypes/audit-question-families/families.py`:
`PASSAGE`, `ANCHORS`, `Journey.view/save_draft/submit`, its fixture and the
existing 12-test family tracer. That experiment already projects fixed spans
onto multi options and delegates scoring. Its passage is hardcoded, it lacks
an accepted source/binding revision, and it refuses practice. The new tracer
keeps the same response projection, adds owner-backed source resolution, and
uses actual practice/exam/diagnostic modes without an exam transport substitute.

Read AGENTS, EXEC-CONTEXT, current STATE entries, AGENT-WORKFLOW reading and
binding-decision rules, SOURCE-TO-COURSE durable reading and staged/checker
contracts, A2 P3 and remaining-audit F3. Sampled `course.accepted_reading_graph`,
`course.validate_reading_source`, `graph.enroll_binding`, permanent binding and
source-ref validation, `journal` link/move/edit/rights/CAS operations,
`auditor.normalize_source`, `identity.object_fingerprint`, `model` content
fingerprint, and runtime/session public, submit, next and report symbols.
Large production modules were not read whole. No web/product survey was needed
for this bounded contract experiment.

## Exact decisions for review

| Code | Proposed v1 decision |
| --- | --- |
| D1 | Add one optional per-item `[EVIDENCE-ANCHORS: <JSON>]` declaration to existing `multi`. Closed fields: `version`, `binding_ref`, `source_ref`, `source_bytes_fingerprint`, `offset_unit`, `passage_fingerprint`, `anchors`. No new question type, parser or scorer. |
| D2 | Reuse permanent `binding_id` and `binding_revision_id`. The item objective must equal that binding's objective. Reuse the existing closed reading `source_ref`: source object ID, accepted source fingerprint, authored locator and one normalized span, including paired adapter locator ID/sidecar fingerprint where present. The accepted graph and journal resolve identity. Filenames never supply identity. |
| D3 | `offset_unit` is exactly `unicode-code-point`. Offsets are nonempty, zero-based, half-open `[start,end)` ranges within the exact normalized span's `verbatim` string. No trimming, Unicode normalization, quote-search relocation or UTF-16 indexing. Pin both SHA-256 UTF-8 passage bytes and original source bytes. |
| D4 | One to 64 disjoint anchors; each is exactly `{id,option,label,start,end,quote}`. Anchor IDs are unique nonempty lowercase ASCII tokens from letters, digits and hyphen, at most 64 characters, scoped to this declaration. Option keys form a bijection onto all existing multi options. Quote is an exact slice. Duplicate labels and duplicate quote text are valid when IDs and offsets differ. Touching ranges are allowed; overlap is refused. |
| D5 | Drafts retain original anchor IDs, item reference and declaration revision. Scoring transport remains an array of multi option keys. Source, binding, declaration or bank conflicts refuse before an attempt and retain original input. A registered move of identical bytes preserves source and anchor identity. New accepted content needs a reviewed new declaration revision; no evidence transfer or automatic re-anchoring. |

`prototypes/evidence-anchor-contract-20260930/declaration.example.json` is the
complete concrete specimen. Placeholder IDs are explicitly illustrative. The
executable tracer enrolls real permanent binding IDs into an accepted synthetic
graph, validates accepted read rights/source bytes through the existing owner,
and records only presentation drafts through the existing journal.

The fictional passage is `Café 🧭: Add two. Start at three. Add two.` Anchors A
and C have equal labels and quotes, but IDs `rule-first` and `rule-second` and
ranges 8:16 and 33:41. B is `start`, 17:32. Both question items are ordinary
multi fixtures. Core meaning is present in plain Markdown with a range table;
native controls expose the exact occurrence, not color or pointer highlighting.

Operational finding: `identity.object_fingerprint` normalizes line endings,
while the normalized passage retains original decoded text. An LF-to-CRLF
conversion can leave the accepted source fingerprint equal and change a slice.
Keep `source_bytes_fingerprint` as a second exact pin. Do not change the shared
identity owner's existing fingerprint semantics for this feature. The raw-byte
pin and passage pin both fail closed in the new tracer.

## Executable proof

Final commands from the repository root:

```sh
python3 tests/evidence_anchor_contract_roundtrip.py
python3 tests/a2_question_families_roundtrip.py
python3 itembank.py lint prototypes/evidence-anchor-contract-20260930/fixtures/bank.md
python3 itembank.py guard .
python3 scripts/preflight.py --quick --source-only
```

The new suite passes 13 tests; the reused family suite passes 12. The synthetic
bank has two items, zero errors and zero warnings. Guard reports zero offending
files. An initial guard refusal identified that a synthetic bank still needs
the repository's `fixtures/` route; it was moved there, with no guard exemption.
Quick source-only preflight passes every gate that ran; sample build, full
Python suite, dirty-tree and JavaScript gates were explicitly skipped.

| Gate | Executed result |
| --- | --- |
| Exact text and identity | Unicode/emoji slices, equal-label/equal-quote distinct occurrences, option projection, source ID, objective and binding revision mismatch, passage fingerprint mismatch. |
| Invalid declarations | Version/type/unknown-field refusal, empty anchors, negative/boolean/empty/out-of-range offsets, wrong quote, duplicate ID/option, foreign option, empty label and overlap. No attempt or sitting advancement. |
| Source lifecycle | Journaled same-ID move retains anchors and draft; external changed bytes, LF/CRLF drift, unavailable file, denied read rights and accepted source successor refuse. Restoring original bytes reopens the original selection. |
| Draft and restart | Journal expected-base refusal preserves accepted draft; changed bank/declaration refuses; raw invalid input remains recoverable; a fresh Python interpreter reopens the same ordered anchor IDs/revision with no response evidence or cursor change. `do_next` refreshes its runtime-owned `served_ts`, so reopening is not bytewise read-only. |
| Actual runtime policy | Mock-wrapped existing scorer confirms it is called. Wrong formal selection advances but gives no correctness/why/selection feedback before the second item closes; report correctness is null while active. Practice wrong holds and discloses only selected-option feedback, then correct advances. Diagnostic withholding and whole-sitting release pass. Replayed practice form response-count token refuses before a second event. |

Browser exercise used the disposable loopback server and native Space-key
checkbox activation, Save draft, reload and Submit selection. Saving showed
zero response attempts; reload retained first-rule/initial-state choices; the
runtime marked that pair wrong, held the item, and disclosed only A/B selection
feedback. The final 320px view had document width 320 and scroll width 320.
Labels measured 56.8px high, buttons 44px, and diagnostics summary 56.8px.
The 1280px view also had no horizontal overflow. Saved visual evidence is
`prototypes/evidence-anchor-contract-20260930/practice-320.png`.

Final artifact SHA-256 pins (paths below are relative to the prototype root
unless explicitly rooted at `tests/`):

| Artifact | SHA-256 |
| --- | --- |
| `anchor_contract.py` | `f1e4089fefb6b59ff8366a809b8e69be5e776e3900d7ded01c5e78c633cca90d` |
| `fixtures/bank.md` | `c9fc4de842a1454d971f35130ca36db089fcfe3828960368d0273050effddc8e` |
| `declaration.example.json` | `d8a6d116e0e8d033db37d5d9f52e02a6e62b97b788764d408aa5c5b6cb0e474e` |
| `tests/evidence_anchor_contract_roundtrip.py` | `4bd51561b81b7ca24c1cbb3a793a320fc362c778b00665ac3ddfead5b7ec3e2c` |
| `practice-320.png` | `1b28ed4cd63a92d4a816213e8fb8865a8fcc7089b28453436f5424f1e8374a43` |

## Minimal production patch after the exact decision is accepted

This is the insertion plan, not permission to edit production files now:

| Owner and symbol | Exact bounded change |
| --- | --- |
| `model.py` directive parsing, lint and `content_fingerprint` | Parse `EVIDENCE-ANCHORS` once as JSON into `q['evidence_anchors']`. Add `evidence_anchor_spec_errors(q)` for closed shape, offsets, quote against pinned passage, disjointness and option bijection. Reject on non-multi, malformed/unresolved source context or duplicate directive. Include the declaration in tested-content hashing so changed mappings cannot resume an old sitting silently. Publish the exact v1 specimen and error codes in the existing spec. Do not recognize this directive as an ignored annotation. |
| Existing course/source owner plus `surfaces/session.py` open/submit | Extract the prototype's pure shape validator into the one model contract; resolve the accepted binding and exact source through the existing course owner. Resolve and validate before starting a sitting and again before serving/submitting this item, including current read rights, locator provenance, exact bytes and declaration revision. Pin per-item declaration/source revisions in the ordinary session; reject stale or unavailable state before the runtime scorer/evidence writer. Coordinate with publication/source writers or validate under their existing locking protocol to close the source-read/submit race. No source lookup by bank filename. |
| `runtime.public_item`, existing session schema/projection | Add only validated public passage, anchor ID/option/label/range/quote and declaration revision. Preserve existing multi `response_schema`. Snapshot pin needs an additive session upgrade with absent legacy field, not inferred source bindings. `score_response` stays unchanged. Pass normalized option arrays through ordinary submit. Canonical evidence remains the existing item/option response; attach an optional declaration revision pin through that evidence owner only if accepted as part of implementation. Never store a second anchor score. |
| Existing quiz/session clients and reviewed proposal owner | Render native labeled checkboxes with visible occurrence ranges and a plain static table. Persist existing client draft against item and declaration revision; display a conflict preserving raw IDs on stale/unavailable source. Use current response/action tokens for replay refusal. Reviewed header changes go through existing proposal preview, expected-base journal acceptance, cancellation and exact undo. Legacy items are unchanged. |
| Existing format/export/package owners | Update the additive public/schema/spec contract; offline static HTML may use only the validated pinned passage snapshot, while served sessions recheck the source. If the exporter cannot validate the exact source/binding/rights, refuse before writing and name served recovery. Validate portable source/locator inclusion and restored immutable pins in a clean offline synthetic package journey only after the build hold is lifted. No silent orphan source links. |

Required production gates are the new 13-test matrix promoted onto the accepted
parser/runtime/client route, malformed real directive lint, source-read/submit
race and crash refusal, additive legacy session upgrade, public schema and
formal DOM/CSS-off leak checks, reviewed header accept/cancel/stale/undo,
cross-process draft reopen, restore identity/locator provenance, and native
keyboard/narrow/high-contrast/reduced-motion checks. Representative human
screen-reader, touch and task-equivalence review must sign its own gate. These
are implementation acceptance gates, not a new research-only successor note.

## Recovery, limitations and review boundary

Durable object: proposed per-item anchor declaration and its source/binding
revision. Owner: accepted bank under model contract, source/graph/journal under
existing owners. Read/write roots for this run: assigned prototype directory,
one new test and this report, plus newly created temporary fictional roots.
Rights: fictional source grants declared locally. Remote egress: none; browser
and server use loopback only. Prototype acceptance applies to synthetic test
fixtures, not the proposed production grammar. Draft journal supports existing
CAS recovery and before images. Retain the original sitting and sidecar on any
source or declaration conflict; restore the exact source bytes or review a new
declaration. Do not map an old anchor selection to a new revision automatically.

The tracer is deliberately single-process. It proves source lifecycle refusal,
not locked cross-process source mutation plus runtime publication. It creates
accepted fictional course/source bindings but does not test a production
anchor-header proposal or production session-schema migration. Browser keyboard
and geometry evidence does not self-certify screen-reader, physical touch,
human preference, learning efficacy or installed-app acceptance. First-error
grading and learner-drawn/free spans need separate semantics and remain open.

No production parser/runtime/evidence/client/schema or shared owner document
was edited. No build/archive/install/release, full preflight, push, worktree
creation or real learner-data access occurred. The parent released writes only
after handoff `b1a96707d668f5d49ebc4838c27ea6d9247fa737`. Other lanes' work was
preserved. Recovery for the committed readiness proposal is a scoped inverse
change to its named files after coordination; never reset the shared checkout.

Direct review question: accept D1-D5 and the exact JSON specimen as the bounded
fixed-span v1 production contract, or name the field/offset/revision rule to
change. The installed sitting and fresh-build hold remain protected either way.
