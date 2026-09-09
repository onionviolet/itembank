# Competition prototype review

Date: 2026-09-08. Scope: `prototypes/competition/{grounding.py,test_grounding.py,server.py,index.html,THIRD_PARTY_NOTICES.md,LICENSE-DeepTutor.txt}` only. Status: review findings, no implementation change.

## Verdict

The fixed server is read-only and uses only the synthetic constant. I found no path that writes evidence, sends a model request, returns an assessment key, or creates a score or accepted revision. The wording in the page and module docstrings accurately limits the current prototype to preparing source context.

`python3 prototypes/competition/test_grounding.py` passed: 17 tests. The test suite does not exercise the browser-to-server selection contract, which leaves the first two findings undetected.

## Findings

### P1. UI selection is reduced to text, so it cannot preserve the selected canonical occurrence

The grounding builder correctly requires a canonical pair of offsets when a selected string has duplicates ([grounding.py:169-179](../../../prototypes/competition/grounding.py#L169-L179)). The browser collects only `Selection.toString()` ([index.html:24](../../../prototypes/competition/index.html#L24)) and posts only `selection` and `revision` ([index.html:27](../../../prototypes/competition/index.html#L27)). The server does not accept or forward offsets ([server.py:55-65](../../../prototypes/competition/server.py#L55-L65)).

This already fails on the fixed source when the learner selects either occurrence of `readings`: the server returns `ambiguous_selection`, even though the browser knows which occurrence was selected. More importantly, a later source replacement could cause a selected phrase to be rejected or require the learner to alter it, rather than carrying the browser's exact, canonical span forward.

Fix: derive UTF-16 or clearly specified code-point offsets relative to `#source`, translate them to the trusted source's canonical offsets, send both offsets, and pass them through to `build_grounded_payload`. Add a browser or server contract test that selects each occurrence of a duplicate phrase and asserts the returned `selection_start` and `selection_end` match the chosen occurrence.

### P2. The alleged remote-target allowlist is only a boolean approval

The docstring calls `allow_remote_target` an allowlist gate ([grounding.py:126-131](../../../prototypes/competition/grounding.py#L126-L131)), but any nonempty caller-controlled string passes whenever the boolean is true ([grounding.py:150-155](../../../prototypes/competition/grounding.py#L150-L155)) and is returned in the payload ([grounding.py:193-194](../../../prototypes/competition/grounding.py#L193-L194)). There is no configured target set, manifest identity, or equality check.

The present server never supplies `remote_target`, so no egress occurs now. The completion claim is still misleading: this is a separate yes or no approval, not an allowlist. A future caller could label an arbitrary destination as approved.

Fix: replace the boolean with an operation-scoped, immutable allowed-target collection or a target identifier resolved by the server. Reject a nonmember before creating the payload. Add a test that approves one target and rejects another.

### P2. Context has no canonical window bounds

The payload includes source-relative selection bounds ([grounding.py:183-191](../../../prototypes/competition/grounding.py#L183-L191)), but `_window` returns only a string ([grounding.py:100-108](../../../prototypes/competition/grounding.py#L100-L108)). A downstream consumer cannot prove which source interval `surrounding_context` represents, place the selection in that window, or retain an exact context locator without reimplementing the window calculation.

This does not allow a false score or accepted artifact. It does weaken the stated selection-plus-window grounding contract and makes a later remote or review record less auditable.

Fix: return and payload `context_start` and `context_end`, both source-relative code-point offsets, with the context string. Test a near-start, middle, and near-end selection, including that the selection span lies within the context bounds and that the slice equals the returned context.

## Rights and notices check

`THIRD_PARTY_NOTICES.md` names the upstream file, pinned DeepTutor revision, copyright holder, Apache-2.0 license, and the copied license text. That is adequate for this bounded adaptation on its face. Before any distribution or broader copy, inspect the exact upstream file's headers and preserve any additional notices.

No claim in the reviewed files says the prototype is a complete tutor, proof of learning, a scored activity, or a recovered course artifact. Keep that restraint when expanding it.

## Re-review disposition, 2026-09-08

`python3 prototypes/competition/test_grounding.py` now passes 20 tests.

| Prior finding | Disposition | Verified evidence | Exact remaining limitation |
| --- | --- | --- | --- |
| P1, duplicate selection lacks canonical occurrence | **Fixed for the fixed synthetic source.** | The browser now counts source-relative Unicode code points, sends `selection_start` and `selection_end` ([index.html:22-28](../../../prototypes/competition/index.html#L22-L28)), and the server forwards them ([server.py:60-67](../../../prototypes/competition/server.py#L60-L67)). The grounding check admits only a matching canonical range ([grounding.py:194-207](../../../prototypes/competition/grounding.py#L194-L207)). | The offset conversion relies on the complete source being a single text node in `#source`. Any later rich reader that inserts markup, hidden text, annotations, or transformed whitespace needs a specified source-to-DOM offset map and an integration test. |
| P2, remote target is a boolean rather than an allowlist | **Fixed in the payload builder.** | `approved_remote_targets` is a typed collection of absolute HTTP(S) URLs and `remote_target` must be an exact member ([grounding.py:142-182](../../../prototypes/competition/grounding.py#L142-L182)). | The prototype has no remote caller. A later selective lesson-generation operation still needs an immutable, user-approved operation manifest to supply this collection and disclose the selected target before egress. |
| P2, context lacks canonical window bounds | **Fixed.** | `_window` returns source-relative start and end offsets, and the payload includes `window_start`, `window_end`, and the matching slice ([grounding.py:102-110](../../../prototypes/competition/grounding.py#L102-L110), [grounding.py:211-223](../../../prototypes/competition/grounding.py#L211-L223)). | The browser shows selection bounds but not window bounds. That is acceptable for this context-preview prototype. Any saved review or remote-generation record must persist both bounds with the source fingerprint. |

The current selective lesson-generation direction is narrower than classroom delivery or autonomous agents. Nothing in this prototype establishes either capability. Its verified role remains: prepare a bounded, fingerprinted source passage for a separately authorized next operation.
