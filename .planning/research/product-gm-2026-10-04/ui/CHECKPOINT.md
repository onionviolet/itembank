# UI GM checkpoint

STATUS: source released for integration

Objective: finish frozen U1-U3 in REPORT.md through implementation, actual
native Chrome inspection, targeted checks and repair, then release source to
integration. Current delegated authorization permits bounded internal workers
only and no Git/publication/install/private learner mutations.

Input: HEAD 28bf561 plus dirty input hashes and source snapshots under
`.reasonix/product-gm-ui-20261004/before/`. Baseline capture passed 30 native
views; screenshots inspected for lesson desktop/390 and reader390.

Ownership: parent owns reading_desk presentation and UI report/capture/checkpoint.
Lesson worker will own only lesson.py and distinctly prefixed lesson tests.
All nine packet reservations remain with UI until explicit release. Shared
daemon/course wiring and broad gate belong to integration. Preserve others.

Completed: frozen U1-U3, actual before/release screenshots (30 views each),
joined final Chrome journey at 1280/390/320, source/JS focused checks, independent
review and all three scoped repairs. Final source input hashes match release
receipt. Only lesson.py and reading_desk.py changed among nine reserved paths.
No broad gate started. Shared legacy golden/assertion updates remain REPORT S3.

No active writer, owned daemon, browser or synthetic preview process remains.
Lesson worker and reviewer are finished. Source and new tests are released to
integration; the full release path list and hashes are in REPORT.md. Source
remains uncommitted, not packaged, not installed and not human-accepted.

Final production SHA-256: lesson.py
77dd3fcab85db682f9ecfe1c0028e885e4f22100af87cda23b55a7b288d7dcca;
reading_desk.py
0b6fddc95880c5323f0557b8930b8fae184cb89153c3a4395a0a213cc5db559d.

Next action belongs to integration: reconcile S3 compatibility assertions, then
run the sole broad gate after all remaining lanes release. S1/S2 shared requests
remain explicit. UI lane has no further frozen unblocked implementation work.
