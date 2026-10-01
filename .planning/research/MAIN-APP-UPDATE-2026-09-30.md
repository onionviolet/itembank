# Main integration and local app update, September 30

The user authorized putting all finished work into main, compiling the latest
app, updating the local app and deleting redundant files. This supersedes the
earlier build/install hold for this candidate. It does not accept pending
question-domain, anchor or activity-graph formats or human learning outcomes.

## Integrated source

All C/D/A and UI owners froze and released their paths. Main now contains:

| Commit | Scope |
| --- | --- |
| `584b0eb` | Native reading-workspace refinement and preserved visual prototype/recovery evidence |
| `ff1a39e` | Exact-domain mechanisms and tests, retained as proposals |
| `f3408dd` | Older audit census, crosswalk and backend opportunities |
| `baa8284` | Fresh-root merge-copy, author-request recovery, selected-context search and shared current-state records |
| `6ee4054` | Final DMG checksum refresh without rebuilding the verified archive |

The runtime production payload was built from `baa8284`. Subsequent changes
affect development packaging tooling and this record only. The portable archive
was rechecked against current shipping files: no missing or changed members.
Normal main push included all preceding R/P3/P5 source commits. No public
release tag or version bump is part of this local update; version remains 0.5.0.

## Verification and installed result

The coordinator's one frozen source run covered 189 Python scripts and the JS
gate; final affected source repairs also have focused evidence. This task ran
the previously deferred packaging, offline math and clean-root package tests,
including clean offline restore and served question/review/recovery journeys.
Quick full-mode preflight passed every gate it runs. Large modules were reviewed
by changed symbols and sampled diffs, not read in full.

`scripts/build_shell_macos.sh` completed. Strict deep signature verification and
DMG verification pass. A concrete checksum defect was found: the portable build
wrote the manifest before the final DMG replaced older bytes. The build now
refreshes checksums after installer creation. A synthetic regression replaces
the installer and proves the refresh names final bytes without changing the
runtime archive. The packaging suite and quick gates pass after that fix.

Native candidate checks used a disposable motion course: Home, course overview,
reading view, source context, retained draft, return to passage and local note
save were directly observed. The installed app was backed up and replaced;
its native shell and frozen sidecar match the verified candidate hashes. The
updated installed Home displays the existing eleven-course workspace and saved
sittings. Its loopback health marker responds successfully. A before/after
manifest of 537 protected Markdown, JSON, JSONL and journal snapshot files,
including linked course roots, has zero changed paths. No real question was
submitted or learner course edited.

| Artifact | SHA-256 |
| --- | --- |
| Portable archive | `4be5fa637322327df44581607b0a5a02246dfd8dd9f31aac98eaa7c32e65169b` |
| Installed frozen sidecar | `06ec4303ee6ee1d946fd7c6c8485d4ab4ecd413dcab92b503eabc5ef24902a51` |
| Installed native shell | `dfeef3d81f5b914320ee52358c69a556c5317a3a8cab7a6aa36e7b7bf593d7f8` |

The final distribution checksum manifest verifies every listed file. Logs,
source snapshots, protected-file fingerprints and the no-drift archive report
are machine-local under `.reasonix/main-app-update-20260930/`. Remote CI owns
the combined final-HEAD and CI-only checks; inspect its actual run outcome,
not the source-only coordinator result, before claiming those gates.

The first source CI run reached the pinned LTI harness and failed because its
page assertion matched the new feedback consumer's JavaScript property name
`answer_text`, rather than an embedded keyed value. The assertion now refuses
serialized answer payloads while retaining the exact public-item and gated
feedback HTTP checks. All 24 LTI checks pass locally with the same pinned
cryptography/PyJWT dependencies. This correction changes tests only, so it
does not alter installed runtime bytes. The superseded pre-repair run was
cancelled; the final main run remains the authoritative combined gate.

## Cleanup and recovery

Removed from active build locations through recoverable Trash: the 2.2 GiB
Rust target tree, PyInstaller work/spec directories, duplicate frozen sidecar,
old v0.5.0 distribution directory and pre-drag-fix app bundle. This moves
roughly 2.3 GiB out of the checkout, not an emptied-Trash free-space claim.
The current app, DMG, portable archives, reusable build environment, source
audits, prototypes, recovery patches and unique diagnostic evidence remain.
The distribution directory is approximately 128 MiB after cleanup.

The prior installed app and workspace snapshot are retained in the local app
backup directory `itembank/app-backups/20260930-main-update`. Restore that
bundle while the installed shell and its own child are stopped to roll back.
Do not overwrite course/session data or remove audit evidence to roll back
the app. App-build and local-install gates are now fulfilled for this bounded
candidate; human visual preference, touch/screen-reader review, learning
efficacy, live external providers and unaccepted formats remain separate.
