# A4 source and recovery implementation

Date: 2026-09-29. Status: native source-level seams and focused synthetic proof, ready for A5 integration review. No commit, push, branch switch, install, release, real learner-file mutation or external account write occurred. The shared dirty checkout was preserved. This record does not accept every CAP-06/07/15/24 capability or claim a live companion, packaged journey or human accessibility acceptance.

## Implemented behavior

- **F1, explicit inclusion:** `source_adapters.write_context_scope`, `read_context_scope` and `resolve_context_scope` persist a private, versioned, course-specific component through the existing CAS journal. Each source inclusion names source ID, accepted fingerprint and exact locator. Notes require explicit IDs and their accepted document fingerprint. New inventory does not change inclusion. Repeating the same accepted selection is a no-op. Resolution returns no source or note content if any selected input fails. Local advisory context requires source read, quote and transform grants; it calls no provider and grants no remote processing. Notes stay labeled learner notes. This is a Python integration seam, not a wired model request or user-facing selection control.
- **F2, exact note return and transfer:** `notes.resolve_source_note` uses the existing exact locator resolver and checks the quoted context hash. `transfer_source_note` supports separate native local `link` and `copy` actions. Link retains an anchor without the source wording. Copy creates a draft quote note only with an explicit quote grant. Both retain source identity, fingerprint and occurrence, give the note its own identity, require the destination base, recheck the source under the note journal's precommit validator, and use the existing paired note writer. Cancel and denied or unknown rights do not create a destination. The companion API is not involved. Existing private-note Markdown remains readable if provider access disappears or an anchor becomes stale.
- **F3, restore conflicts:** ordinary `course_package.restore_package` now validates every destination identity, path, accepted fingerprint and current on-disk state before writing its first object. A matching registry fingerprint no longer hides externally changed disk bytes. An unregistered destination draft blocks the whole preflight rather than leaving earlier course writes. Ordinary evidence replay is preflighted through the existing writer whenever evidence is carried, extending the prior reading-only check. Reading transport still uses its existing staged atomic publication and private-note consent rules.

## Reconciliation and measured gates

Read the parallel ownership packet, live AGENTS instructions, `.planning/EXEC-CONTEXT.md`, current STATE front section, AGENT-WORKFLOW, source-research lane, Open Notebook INTEGRATION/FORKS/UI-FORK-AUDIT, the 17C restore audit, and scoped SOURCE-TO-COURSE reading/authority sections. Sampled symbols and windows in notes, source adapters, identity, journal, package and their tests. Large modules were not read whole. Historical recovery memory was a search pointer; live modules and passing tests supplied the conclusions.

The existing exact-locator implementation already distinguishes duplicate text by locator ID, validates accepted bytes and sidecars, and checks read rights. It was retained rather than replaced. Existing reading-package tests already prove consent-separated current/private-note history backup, editable Markdown, restart return, adapted locator companions, rights restrictions, orphan history losses, interruption and offline restore. Those proofs were rerun, not treated as unimplemented features.

| Command | Actual result |
| --- | --- |
| `python3 tests/a4_source_recovery_roundtrip.py` | Exit 0, 7 tests, final run 0.104 seconds. Persist/reload explicit inclusion, excluded-source sentinel absent, second occurrence at line 4, note edit/reopen, local provider-free context, unknown transform refusal, separate link/copy identities, quote denial/unknown refusal, cancel without writes, byte-exact paired undo, changed note/source refusal, extraction failure preservation, stale restored disk refusal and later destination draft conflict without earlier writes. |
| `python3 tests/source_locator_resolution_roundtrip.py` | Exit 0, 2 tests. Existing duplicate locator, changed revision and sidecar conflict proofs. |
| `python3 tests/source_adapters_roundtrip.py` | Exit 0. Existing Markdown/PDF/DOCX/PPTX/web/transcript/OCR/EPUB gold cases, paired recovery, rights, locator and degraded-ASR checks passed. A PDF font warning appeared. OCR tests use a stub, not live model acceptance. |
| `python3 tests/reading_package_roundtrip.py` | Exit 0, 14 tests, 1.741 seconds. Existing clean offline reading, private-note and companion transport proofs passed. |
| `python3 tests/course_package_roundtrip.py` | Exit 0. Manifest/losses, clean restore, archive containment, rights/evidence drift and snapshot checks passed after restore changes. |
| `python3 tests/note_trio_roundtrip.py` | Exit 0, 9 passed. |
| `python3 tests/open_notebook_roundtrip.py` | Exit 0, 4 tests. Companion health tests are mocked, not a real service. |
| `python3 tests/note_schema_roundtrip.py` | Exit 1, 7 passed and 1 failed. Repository guard found `prototypes/audit-question-families/bank.md`, a concurrent A2-owned four-item bank outside A4. |
| `python3 tests/note_promotion_roundtrip.py` | Exit 1, 7 passed and 1 failed. Shared settings hash was `3c86b51885dee9b3e42d81af0c5fd7c4671f4cfadce51e5c4bdad7cd73ca31ed`, versus suite baseline `b6e5b15484ce247f96b69f18df73da45e109a38e0c29aa0d6ad63093e54edc2a`. No A4 settings or promotion changes. |
| `git diff --check` scoped to A4 modules and test | Exit 0. |

Development-only failures were corrected: the first new-suite run had three missing destination-root errors; a subsequent run changed only a note companion and met the existing journal primary `no_change` refusal; the final added conflict fixture initially lacked a package grant and was correctly excluded. Final synthetic fixtures explicitly create approved restore roots, edit note records with wording and grant the lesson package right. A lookup of nonexistent `tests/note_document_roundtrip.py` exited 2; the real note suites above replaced it. Existing schema resource file warnings were left with their owner.

Measured extraction fixture: Markdown heading, `E = mc^2`, and a two-column table returned byte-identical preview Markdown, zero unsupported rows, and mapped span IDs for every locator. Invalid UTF-8 returned `unsupported` and a byte snapshot proved that preview changed no source or journal files. This is a narrow native success and an honest refusal, not a PDF layout/equation benchmark. No measured new fidelity defect justified adding Docling, MinerU, Marker or Unstructured; no extractor, model or donor dependency was installed.

## Live-service gate and retained limits

**R1, Open Notebook blocked:** `command -v docker` found no command, `curl --max-time 2 -sS http://127.0.0.1:5055/health` exited 7 (connection refused), and the bounded approved local code-root search found no Open Notebook pyproject/compose checkout. The existing audit pin is upstream `3127f14ea9dbb519f0e4ddc64a0742ca644ba6ef`; no disposable service at that pin ran here. Health repair remains source/mocked proof only. No read-only REST object client or external note transfer was enabled because real instance identity, OpenAPI response shape, authentication and notebook ownership remain unproved. Revisit with an already available pinned disposable service, then read-only objects, provider trial, reviewed transfer and restart/undo in that order. A healthy port alone cannot release this gate.

**R2, remaining recovery and product gates:** the new scope is private operation state, not a canonical course source or automatic export inclusion. Exporting it needs explicit personal-backup scope and a named omission if excluded. A5 must prove a connected selected-context request and transferred-note clean restore before claiming the full new journey accepted. Ordinary restore now refuses known conflicts before writes, but unlike reading transport it still performs per-object journal transactions after preflight; a later disk failure or race is not whole-root atomic publication. Existing journal recovery remains the authority. Full general restore staging is a retained gate, not claimed by these tests. Human keyboard, touch, screen-reader and learner efficacy checks, packaged and installed-app checks, and provider-authentication checks remain unrun.

Objective-dependent media extraction, live OCR, ASR and alternative retrieval remain registered/backburner: revisit on an approved objective requiring them and a measured native reading/locator failure. Live model/provider seams depend on explicit rights/egress and a synthetic trial. Automatic two-way companion sync, remote SSO and broad desktop-fork absorption remain deferred to their existing owners and triggers.

## A5 integration request

**A1:** wire the native scope seam to the existing approved operation roots and local advisory request owner. Preview included source occurrences, separate learner notes and excluded count before saving; use expected scope and note fingerprints. Resolve immediately before using context, refuse conflicts without falling back to broad discovery, and keep remote processing separately authorized. Do not pass trusted Python validators from request JSON. Keep the scope root distinct from the private notes root because note reads take that root's journal lock.

**A2:** use `resolve_locator` for the source preview and `transfer_source_note` for an explicit Link or Copy quote control. Destination is the existing course private-note root. Show draft role, source ID, accepted fingerprint, exact locator, rights, destination and undo before confirmation. Retain unsaved wording on refusal. Prove the copied note through existing private-note export/clean restore, then source citation return. Do not describe the local quote-copy seam as a verified Open Notebook API transfer.

**A3:** address the shared A2 bank guard and settings fingerprint failure with their owners before the final combined full preflight. No full preflight ran in A4. The existing note writer also refuses a Markdown-only edit when its primary JSON bytes do not change; a future UI integration should edit the actual note record with its Markdown projection or request a journal-owned companion-only change, not bypass the writer.

## Fingerprints and recovery

Base dispatch HEAD: `8ccd45832b66b0b86bb406d6232ef0633ef71dc3`. Owned production paths were initially clean even though many other paths were dirty. Before snapshots were copied to the session-local `/tmp/itembank-a4-before-20260929/` before the first edit. The evidence and new test did not exist before A4. Recover by reviewing and reverting only this lane's diff, or using those before snapshots after confirming the current hash still matches this lane; never overwrite a later writer.

| Path | Before SHA-256 | After SHA-256 |
| --- | --- | --- |
| `notes.py` | `ab88f4a60013688615459e690339106aba7d459cdf9db309eaf16c7e8963d2d2` | `e43c6f9db337451bed8c80383c52edee81022f0282d595c26411f56fbd8249f1` |
| `source_adapters.py` | `cd1051d0105c565cf80e43a402c373f4e6ecbf79cc05d642b7dd581803d9eb1b` | `4d008b598a1619db50a2b8dd0bb5ecc8a936c900e3cfae60c647119bdd482b00` |
| `course_package.py` | `758b86227c8b59eefd62c1cfe7515c7cb9aed553f98ee1b347e0e39b0e836ed4` | `76f1afa21592eefc2fba391ff43720a824190de5c4ffe9ee077688f10483dd4f` |
| `surfaces/open_notebook.py` | `9ea16cee880a81198aac4f9dd4f11c62aeb56dea9410f4e8b975a3c938430f52` | unchanged |
| `tests/a4_source_recovery_roundtrip.py` | absent | `148438cc96483689d7e58eb3b78a39ff8f681103d005357032e118254c375f63` |

No shared daemon, course, journal, parser, scorer, schema, A3 file, STATE or README was edited.
