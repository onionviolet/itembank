# Vendored CodeMirror 6 — supply-chain record (Directive §4a)

**Vendored:** 2026-08-11, by plan 05-05 Task 2 (ruling 5/11: CM6 is the editor;
ruling 16: a JS test runner is taken). The served quiz page embeds this local
bundle; it never loads an editor from a CDN.

## What is vendored

`assets/vendor/codemirror/codemirror.bundle.js` — one self-contained IIFE
exposing the global `CodeMirror` with exactly the API the page's boot script
consumes: `EditorState`, `EditorView`, `Compartment`, `keymap`, `lineNumbers`,
`placeholder`, `history`, `historyKeymap`, `undo`, `redo`, `insertTab`, and
`lineWrapping` (the no-wrap facet value, exposed for the test's structural
assertion).

`assets/vendor/codemirror/check-editor-boot.js` — the ONE place the check
editor is configured (line numbers, Tab/Shift-Tab/Enter keymap with a
read-only guard, placeholder, no wrap). The served page embeds it after the
bundle; `tests/js/check_editor.test.mjs` loads the same two files into jsdom,
so the interactive contract is executed rather than read from source. SHA-256:
`9cfa9c625d6d7b0caf2a0787d8f98bbcbf52c8e16e3c5d81583dcea72d03ffa8`.

## Pinned upstream packages (the bundle's contents)

| Package | Version | License |
|---|---|---|
| `@codemirror/state` | 6.7.1 | MIT |
| `@codemirror/view` | 6.43.8 | MIT |
| `@codemirror/commands` | 6.10.4 | MIT |
| `@codemirror/language` (transitive via commands) | 6.12.4 | MIT |
| `@lezer/common` (transitive) | 1.5.2 | MIT |
| `@lezer/highlight` (transitive) | 1.2.3 | MIT |
| `crelt` (transitive) | 1.0.7 | MIT |
| `style-mod` (transitive) | 4.1.3 | MIT |
| `w3c-keyname` (transitive) | 2.2.8 | MIT |
| `@marijn/find-cluster-break` (transitive) | 1.0.3 | MIT |

All ten packages are published by Marijn Haverbeke's CodeMirror organisation
(and its immediate dependency authors) under the MIT license. Upstream project:
<https://github.com/codemirror/dev>; package sources under
<https://code.haverbeke.berlin/codemirror/>.

## Immutable refs and integrity

The three top-level packages were installed at exact pinned versions from the
npm registry (`npm install @codemirror/state@6.7.1 @codemirror/view@6.43.8
@codemirror/commands@6.10.4`); the transitive set is the resolved dependency
closure of those pins (no `^`/`~` ranges were accepted for the top-level three).
The registry published tarball shasums at fetch time:

- `@codemirror/state@6.7.1` — shasum `9e88a17448c1dbc7b50acbeeec979ed7ccf1d6fc`
- `@codemirror/view@6.43.8` — shasum `c211dc77aca139ecc51aff7712c0c4a32cc5f74a`
- `@codemirror/commands@6.10.4` — shasum `64dec1bd043976eb344e3cc9d15af13b6f724bfd`

**Bundle SHA-256** (the committed file, recomputed by
`tests/check_roundtrip.py`'s vendor-integrity assertion):

```
58de2c136ca4bbfd92a08e50d64884708109fd3d18843fc1c47dce6e657be588  assets/vendor/codemirror/codemirror.bundle.js
```

## License review (dated)

Reviewed 2026-08-11: every package in the pinned set above declares the MIT
license in its `package.json`; the upstream project is the well-known
CodeMirror editor maintained by Marijn Haverbeke. MIT permits vendoring,
modification and redistribution with the license notice retained; the license
texts remain in the upstream packages (not shipped in this repo), and this
record names the upstream project so provenance is traceable. No proprietary,
GPL, or other copyleft license appears in the closure.

## How the bundle was produced

1. `npm install` the pinned top-level packages (above) into a scratch
   directory outside the repository.
2. `esbuild entry.js --bundle --format=iife --global-name=CodeMirror --minify`
   where `entry.js` re-exports the ten names above.
3. Commit the single output file; the scratch directory and esbuild are
   build-time only and are not part of the repository.

To re-vendor (a future bump): repeat steps 1-3 with new pinned versions, record
the new version set and SHA-256 here, and update the integrity assertion in
`tests/check_roundtrip.py`.

## What invalidates this record

A change to `assets/vendor/codemirror/codemirror.bundle.js` without a
corresponding update of the SHA-256 above, or any page reference to a CDN URL
for the editor.

## The JS test runner (ruling 16)

`tests/js/check_editor.test.mjs` runs under Node's built-in `node --test`
against the **real vendored bundle and boot script** loaded into jsdom — the
keyboard contract is executed, not inferred from source. The DOM provider is
pinned and locked:

| Package | Version | License | Pinned by |
|---|---|---|---|
| `jsdom` | 29.1.1 | MIT | `tests/js/package.json` + `tests/js/package-lock.json` (committed) |
| Node's own test runner | the repo's CI Node | MIT | `node --test tests/js/` in CI |

The lockfile records the integrity hash of every resolved package, so `npm ci`
in `tests/js/` reproduces the same 39-package closure. jsdom is MIT-licensed
(project: <https://github.com/jsdom/jsdom>); it is a test-time dependency
only — the served page never loads it. License reviewed 2026-08-11 alongside
the bundle above.

