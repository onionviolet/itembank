# UI and resource optimization packet

User request: "fix all concurrently", referring to O1 through O5 in the current audit.

Status: O1 through O5 implemented and verified in source on branch
`codex/ui-resource-optimizations-20260925`. Changes remain uncommitted.
No push or installed-app replacement was requested or performed.

Owner and integrator: current coordinating agent. Existing unrelated edits stay untouched.
The runtime, course operation layer, journal, rights, and accepted files retain their authority.
All verification uses synthetic content and disposable roots.

| ID | Observable outcome | Builder ownership | Gate |
| --- | --- | --- | --- |
| O1 | Course objectives, sources, and evidence open useful contextual details and return paths. | UI worker: course-area portion of surfaces/daemon.py, a dedicated course UI helper if needed, focused course navigation tests. | Real loopback HTTP navigation over a synthetic course, valid destinations, unavailable states, and no keyed disclosure. |
| O2 | Build and review exposes configured source-grounded operations, durable proposals, review, acceptance, rejection, and undo. | UI worker: same course-area ownership, reuse surfaces/agent_operation.py and course_ops authority. | Synthetic proposal to accepted revision and undo through the course workbench, stale conflict refusal, report-only policy, and script-free forms. |
| O3 | Unchanged discovery avoids repeated bank parsing while changes appear immediately. | Discovery worker: new surfaces/discovery_cache.py and focused tests only. Integrator owns daemon scan integration. | Parse-count and timing comparison plus add, remove, rename, same-size replacement, symlink escape, collision, year change, and concurrent refresh checks. |
| O4 | Quiz enhancements process changed content once and preserve presentation behavior. | Rendering worker: surfaces/quiz_page.py and focused JavaScript/Python tests only. | Dynamic replacement and input preview correctness, bounded observer work, hidden-page behavior, existing math and quiz checks. Actual battery savings require energy measurement. |
| O5 | Storage use is visible and explicit cleanup is limited to named rebuildable data. | Integrator: storage module, settings integration after UI worker, developer cleanup command, build inventory, focused tests. | Accurate synthetic category totals, dry-run default, stale/symlink refusal, recoverable cleanup, and preservation of courses, banks, attempts, journals, snapshots, and notes. |

No schema, scorer, grading, disclosure, accepted-content, or remote-egress redesign.
Do not delete existing build output while another build may use it.
No worker commits or stages files. Each returns changed paths, exact checks, and remaining limits.
The integrator reviews actual changes, runs focused gates, then repository preflight.
Full-file reads of large modules are outside scope. Read the named symbols and tests.

## Delivered behavior

| ID | Result |
| --- | --- |
| O1 | Objective, source, and evidence details have contextual destinations and return paths. Activity links require exact current bindings. Saved-session links require one admitted bank path. Source previews are selected explicitly and refuse keyed bank content. |
| O2 | Build and review reuses configured agent operations for proposals, history, bounded diffs, acceptance, rejection, and undo. Accept retains rights, journal, stale-conflict, and report-only enforcement. Undo now handles newly created files correctly. Generation still requires configured agent runs. |
| O3 | A bounded process cache stores file classification without content or keys. Warm navigation retains containment checks and detects edits, replacements, additions, removals, renames, and year changes. A synthetic 100-bank scan measured 102.17 ms cold and 7.71 ms warm, with parser calls falling from 100 to zero. |
| O4 | Quiz math, argument, and LaTeX enhancements coalesce changed subtrees into animation frames. Hidden pages defer this work until visible. Directly inserted math sources and dynamic replacement retain rendering. |
| O5 | Settings exposes on-demand storage accounting and guarded Python-cache cleanup. The CLI has equivalent inspection and cleanup. A developer helper previews Cargo build cleanup and invokes Cargo only after fingerprint, containment, and protected-content checks. Live build output and learner files were not cleaned. |

## Verification and limits

The full preflight ran 141 Python scripts and the JavaScript suite. It found two
missing storage registrations in capability and surface coverage. Both were fixed,
and both checks passed when rerun. The JavaScript suite and all other Python
scripts passed subject to their reported platform and optional-feature skips.
The clean-tree gate failed because this task and concurrent work are uncommitted.
It is not a functional test failure.

After the fixes, quick preflight passed every gate it runs. Final targeted checks
passed for course workbench, agent operations, IA routes, discovery cache and
integration, storage, presentation, capability registration, surface coverage,
quiz observers, and packaging. Packaging exercised the new storage command from
the built Python archive outside the checkout. The Windows onedir sidecar was not
built and its packaging checks were skipped. The two CI-only steps remain CI-only.

Browser review verified course-map anchor navigation and the storage page at
desktop and 320-pixel width. At 320 pixels the storage page had no horizontal
overflow and Settings was the active navigation item. The temporary browser and
preview daemon were closed afterward. This is not human accessibility acceptance.

Actual energy use and battery savings have not been measured. The installed app
has not been replaced. Large existing modules were reviewed by relevant symbols
and diffs, not read in full. Concurrent planning and visual-design work remains
outside this packet and must retain its own verification evidence.
