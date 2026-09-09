# Hands-on evidence

Date: 2026-09-08. Synthetic input only. These observations are not learner evidence.

## OpenMAIC public application

Opened the public Taylor Series Explained classroom `WVgmqzuHKa`. Its nine-scene outline included explanations, an interactive approximation, quizzes, and a summary. Changing the polynomial degree from three to five changed the displayed formula. Completing the two-question quiz produced 25/25. Reload returned to the first scene, but reopening the quiz retained that result.

Requested a short explanation, interactive comparison, and practice question from synthetic rainfall text with 12 mm and 18 mm over equal 24-hour intervals. The request said to use only the source and label extra material as synthesis. Guest generation created classroom `Z6VlGjsoos`, including a teacher, assistant, and classmates. The first scene became usable. It added the millimeter-to-liter conversion, a standard 24-hour interval, and other outside material without the requested synthesis label. Its chart used values beyond the supplied 12 and 18. This is a grounding failure, not a claim that every added fact is false.

The second scene remained generating across multiple observations. Export was disabled at the last observation. Full generation and offline export were not verified. No measured latency or exact guest-credit consumption was captured.

## DeepTutor isolated local application

Installed PyPI DeepTutor 1.6.6 in a temporary virtual environment with a temporary application home. Startup also created default settings, personas, and logs in the launch directory despite that home setting. Those trial-created files were moved intact outside the repository after shutdown. Patched only that temporary launcher's bind address from all interfaces to loopback. Configured the existing local Ollama qwen3.5:4b model with an 8192-token context. No hosted model key or private learner file was supplied.

The same rainfall request in chat completed in a displayed 52 seconds and about 3.1k tokens. The response correctly explained 12, 18, and the 6 mm difference, labeled synthesis, and supplied practice. Its claimed interactive comparison was a static table with an answer, not a manipulable activity. The UI displayed an estimated $0.0007 despite using local Ollama. This is not evidence of a monetary charge.

Uploaded the synthetic text through the local reading API, then created and opened a reader collection through the UI. Selecting “millimeters” enabled contextual assistance. Explain vocabulary eventually returned “This reading action is temporarily unavailable.” The source remained readable. Successful chat does not establish successful reader assistance.

## Scope and fairness

The isolated OpenMAIC outline-package trial made one local Ollama request. A separate single teaching-scene trial exercised `generateSceneContent`. Each reached its 30-second timeout and returned `invalid_model_output` with no candidate. Neither retried. The four deterministic fixture tests are API-contract tests, not proof that live lesson generation succeeds. A successful live teaching artifact remains an open promotion gate.

OpenMAIC used its guest generation configuration. DeepTutor used a small local model in chat with browsing, code, and additional agents discouraged. These are different workloads and model settings. No comparative efficiency score is justified. LiaScript's landing page was inspected, but no completed lesson trial is claimed. No participant learning outcomes or human accessibility review were measured.
