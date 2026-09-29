# Open Notebook in the itembank course workspace

**Status:** integration design and first companion slice, 2026-09-27. `surfaces/open_notebook.py` detects a local API and opens the separate UI from the course Sources area. No notebook data is imported yet, and no live Open Notebook instance has been verified.

## Evidence and fit

Open Notebook is MIT licensed. Its current repository advertises a separate web UI, REST API, local Ollama and oMLX models, OpenAI-compatible endpoints, and hosted API-key providers. The documented development ports are 8502 for its UI and 5055 for its API. It stores notebook sources and notes in its own service and SurrealDB. Its API has notebooks, sources, notes, chat, search, credentials, and health endpoints. The API reference warns that its password header is a development mechanism and that deployment needs stronger authentication.

- Repository and license: https://github.com/lfnovo/open-notebook and https://github.com/lfnovo/open-notebook/blob/main/LICENSE
- API reference: https://github.com/lfnovo/open-notebook/blob/main/docs/7-DEVELOPMENT/api-reference.md
- Provider configuration: https://github.com/lfnovo/open-notebook/blob/main/docs/3-USER-GUIDE/api-configuration.md

Itembank already has `model_adapter.py` transports for a hosted CLI and an OpenAI-compatible endpoint. These drive bounded itembank operations. They do not configure Open Notebook's own models or give itembank authority over Open Notebook's research records. Itembank's course UI has a Sources area but no notebook area. Canonical course files, learner notes, and scored evidence remain under itembank's existing owners.

The current companion checks `http://127.0.0.1:5055/health` when the course Sources area opens. Its link opens `http://127.0.0.1:8502/` in a new tab. Non-default local ports can be set with `ITEMBANK_OPEN_NOTEBOOK_API_PORT` and `ITEMBANK_OPEN_NOTEBOOK_UI_PORT` before starting itembank. The response must be JSON with `status: ok`. This health response confirms a responding local service, not its version, authentication, configured model, or ownership of any notebook. No Open Notebook service was running on port 5055 during this pass.

## Decision for the first integration

Use a **separate local Open Notebook service with an itembank course companion area**. Do not vendor the full app or fork it yet. Keep the upstream code updateable and its data distinct. A fork becomes useful only if the API cannot supply the required course context, accessible tab flow, or reviewed transfer. MIT permits a fork if needed, with its copyright and license retained.

The companion should appear from a course, initially under Sources or as a course tool. It shows connection state and the notebook bound to this course, then opens the research UI in a separate tab or desktop web view. A copied source or note crosses the boundary only through a named import or link action with a preview, citation/provenance, rights check, expected fingerprint, and undo. Importing a note creates a draft learner artifact or lesson proposal. It never creates a scored item or accepted source automatically. A notebook chat response is advisory and cannot settle assessment state.

| Route | Open Notebook can use it now | Itembank handling |
|---|---|---|
| Local model | Ollama, oMLX, or OpenAI-compatible local endpoint | Configure in Open Notebook. Show endpoint and egress as local only after checking the actual address. |
| Paid API | Provider credential or OpenAI-compatible endpoint | Configure in Open Notebook. Disclose which source text leaves the machine for each research operation. |
| Existing AI subscription | Unverified as a supported Open Notebook provider route | Investigate the specific subscription and its authorized interface. Do not assume a chat subscription grants API access or pass browser session credentials to a bridge. Itembank's `hosted_cli` transport alone does not make Open Notebook use that CLI. |

## First vertical slice

1. Expand the current loopback-only port settings into a product connection setting. Keep its password outside `itembank.json`, using an environment variable or OS credential store. Health-check the API without sending any course content. Show disconnected, wrong-version, and authentication-failed states distinctly. The current slice only distinguishes a healthy `{"status":"ok"}` response from unavailable or invalid ports.
2. Add a course companion control that opens a specific linked notebook. The course stores only the external notebook ID and instance identity, not a copied research database. A missing or changed notebook leaves the course usable and exposes a relink action.
3. List the notebook's sources and notes read-only with their Open Notebook IDs and provenance. Establish the actual current API response shape against a pinned upstream revision and a disposable local fixture before writing this client. Do not rely only on the prose API reference, which contains mixed `/api` examples.
4. Add one explicit transfer: select a note or source, preview it, choose link or copy, state rights and destination, validate the resulting itembank object, then commit through the existing journal. Preserve the original Open Notebook ID, source locator, revision/fingerprint, and import timestamp. If the upstream object changes, report stale rather than silently resyncing.
5. Test the local model and API-key routes with synthetic material. Exercise offline, stopped service, bad password, duplicate ID, changed upstream bytes, denied rights, restart, and undo. Run focused itembank tests, then package and inspect the native course flow. Human keyboard, screen-reader, and narrow-screen acceptance remains a separate gate.

## Ownership and recovery

The learner owns both workspaces and chooses whether to transfer material. Open Notebook owns its notebooks, sources, notes, provider credentials, and generated chat. Itembank owns its course manifest, accepted files, evidence, and scoring. The companion's notebook ID is a reference, not a source of truth. Disconnecting Open Notebook does not remove accepted itembank files. Deleting a linked notebook leaves a broken link with a repair path. Automatic two-way sync and importing answer keys are outside the first slice.

## Open questions

- Which existing subscription, if any, should supply model access? Provider terms and a supported technical path must be checked for that exact service.
- Should the first transfer be a notebook note into a learner note, a research source into the course source registry, or both?
- Is the separate tab sufficient for the learner's research flow, or does a tested embedded view materially improve context preservation and accessibility?
