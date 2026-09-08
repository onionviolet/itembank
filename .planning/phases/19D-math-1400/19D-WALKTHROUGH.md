# Phase 19D visible walkthrough

**Scope amendment, 2026-09-08:** the user deferred local AI and waived the new
Math 1400 sitting for now. Rows below remain observed history. Unrun steps are
deferred, not passed, and Phase 20 must not manufacture their evidence.

Launch: `python3 itembank.py daemon /Users/weiwei/Documents/itembank-courses --port 8741 --no-open`

| Step | Start and visible action | Result and durable evidence | Transition judgment |
|---|---|---|---|
| Shelf | Open `/`, then activate `Start Math 1400: OpenStax College Algebra 2e` | Visible shelf card opened opaque course route `/course/95dbccc7716142cc`. Card said `Up to date` and `Not started`. | Pass. No guessed course URL or CLI repair. |
| Course orientation | Read overview and course-area navigation | Visible cue `Current area: Overview`; Learn, Practice, Test, Course map, Sources, Build and review, Agent, and Evidence were present; `Back to courses` was visible. | Pass for route and orientation. Overview was empty before a lesson or bank existed. |
| Source and objective build | Use published 19A operations, then inspect the visible Sources and Course map doors | Source `9645e62714424417`, unit `07c579b90823454e`, objectives `88962d96fe7048bd` and `ddcef5efe9a44762`, and graph revision 8 were durable. | Pass. Rights were explicit and remote processing was denied. |
| Agent | Activate visible `Agent`, then `Start openstax-linear-equations-lesson` | The local `qwen3.5:4b` backend was reached. Attempts `agent-openstax-linear-equations-lesson-e7ba8c402c4c`, `86475a0f042a`, `bf5ff966a109`, `f162374d1a12`, and `e5f04ff65e7f` settled without a proposal. Final code: `adapter.malformed_response`, reason: `endpoint returned no JSON assistant message`. | Blocked. The page retained no proposal row, accepted revision, journal id, or undo control. |
| Accept and undo | Required visible proposal review, accept, undo, byte comparison, and second accept | Not reached. No model bytes entered the course. | Unmet, correctly fail-closed. |
| Learn, Practice, Test, evidence, next activity, home | Required continuous learner journey | Not run because the required generated treatment was not accepted. No real sitting, note, resume record, or recommendation was manufactured. | Unmet. |
| Recovery | Required export, isolated restore, manifest, and replay | Not run because the representative course was incomplete. | Unmet. |

Browser history and focus were checked through the shelf, course, and Agent transitions. The long-running Agent form caused the temporary in-app browser target to close twice. The durable result remained a typed refusal and no unsaved accepted content was lost.
