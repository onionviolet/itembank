# Visual runner repair, October 4

STATUS: source released. The two failed visual runner scripts now pass on the
released lesson source. Integration remains the sole broad-preflight owner.

The combined source-only gate preserved N4/N6 failures in
`.reasonix/product-gm-20261004/integration/preflight-source-only.log`.
Both stopped before the real QA matrix because Playwright's bundled
`chromium_headless_shell-1234` executable was absent. No browser was downloaded.

## Changed source and recovery

`tools/visual_qa.py` now uses one bounded `_launch_browser` helper. An explicit
`ITEMBANK_VISUAL_QA_CHANNEL` stays authoritative. With no configured channel,
the harness first launches bundled Chromium, and falls back to installed
Chrome only for Playwright's typed error whose first line says the executable
does not exist. Permission, sandbox, security, closed-browser and unrelated
errors propagate. A failed Chrome fallback also remains a genuine failure.
The evidence records the requested/selected channel and exact fallback reason.

`tests/product_gm_integration_visual_launcher_roundtrip.py` uses an isolated
launcher AST and standard-library mocks, so selection checks need neither
Playwright nor a browser install. Its eight checks cover explicit channel
selection/refusal, bundled default, empty configuration, missing-bundle
fallback, absent Chrome, other driver errors and non-driver errors.

| Path | Released SHA-256 |
| --- | --- |
| `tools/visual_qa.py` | `cb9459307cf496fe4671040df964b60d4b46dd23181aee81c6e201aadcfba179` |
| `tests/product_gm_integration_visual_launcher_roundtrip.py` | `2f1d3a1bf7335a9464e398256682d82df879ba149f1e8543d40b03f852e336b0` |

The inherited tools base was
`9ccecc9ac1f9ca539c2ada6efca9d0169e86f13dfd278d9d3d4f91b4eca1e126`.
Expected-base publication kept a before-image and recorded prepared/published
operations under `.reasonix/product-gm-20261004/integration/visual-runner/`.
`tools.task.patch` is the task delta. Restore only that reviewed delta against
the current source, preserving later edits. Remove the new test only if its
released hash still matches. No other source path was changed by this worker.

## Actual focused gates

| Gate | Result and receipt |
| --- | --- |
| Launcher selection | Eight standard-library checks passed on the released tools/test hashes. |
| Existing QA preservation | All 14 preexisting QA functions and the matrix call order/arguments are AST-identical. `qa-preservation.json`. |
| Direct default browser matrix | Exit 0; 13 positive gates passed across eight screens, and the hover-only negative failed equivalence as required. `matrix-released.log`, `matrix-released-evidence.json`, `matrix-released.json`. |
| `tests/visual_accessibility_roundtrip.py` | Exit 0; actual driven matrix ran and passed. `accessibility-released.log`, `accessibility-released.json`. |
| `tests/paced_lesson_tracer.py` | Eight scenarios passed, zero failed; actual layout leg ran and passed. `paced.log`, `paced.json`. |

The final real checks pin released `surfaces/lesson.py` at
`d7b8ae144dde7342dd91c6393ae06fa77b2ab272faca966724992b51f1ed2691`.
Each final receipt records current inputs before/after and confirms no drift.
Default launch evidence shows Playwright 1.62.0, bundled executable absent,
and installed Chrome 154.0.8037.95 selected. No assertions or negative control
were skipped. No additional QA defect was observed.

Earlier direct/accessibility checks also passed. Their original receipts are
retained; the final checks extend the source manifest to include the released
lesson and visual fixture inputs, so only the final receipts are used for
integration release. Initial and final direct screenshot hashes are identical.

## Boundaries and next action

This is synthetic source verification through a real development browser.
Packaged/installed itembank behavior, human visual/accessibility acceptance,
and learning efficacy remain separate gates. No broad suite, build, install,
network setting change, private learner mutation or Git operation was run.
Remote egress was not added. Synthetic pages and test state stayed local.

Inspection sampled launcher/main, fixture construction, equivalence checks
and calling test windows. AST comparison verified preservation of the other
QA functions. Parser, scorer and large learner modules were not read in full
or edited.

The worker releases the tools/new-test reservation, with no active child or
process. Integration may freeze these hashes for its combined gate and reuse
the focused receipts for unchanged inputs. Required advertised-LAN and
delivery gates retain their existing state.
