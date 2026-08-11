# Registry-Safety Preconditions — vendored typefaces (plan 03.1-06 Task 1)

**Rule (UI-SPEC Registry Safety / Directive 4a supply chain / KaTeX
`09-03-PLAN.md` precedent):** no byte is fetched until the four preconditions
below are recorded. This file is the record. It was written **before** any
byte was fetched from any URL, and no unofficial URL is ever substituted.

Recorded: 2026-08-10 by the plan 03.1-06 executor.

---

## The four preconditions

### 1. Immutable release tag

| Family | Pinned reference | Immutability basis |
|---|---|---|
| Source Serif 4 | `4.005R` | GitHub release tag `adobe-fonts/source-serif` release 89768054 (`4.005R`), published 2023-01-20, not draft/prerelease, tag target `release` branch |
| iA Writer Quattro | `f32c04c3058a75d7ce28919ce70fe8800817491b` | The upstream repo `iaolo/iA-Fonts` publishes **no release tags** (verified: `/releases` and `/tags` both return `[]`). The last commit on `master` (2023-06-16, GitHub-verified PGP signature, author Oliver Reichenstein) is therefore the pinned immutable ref for this family |

### 2. Published archive SHA-256

GitHub does **not publish a SHA-256** for these assets (release assets expose
`digest: null`; raw files expose only the git **blob SHA-1** content hash).
Recorded honestly as a precondition:

| Family | File | Git blob SHA-1 (published, immutable content hash) | SHA-256 |
|---|---|---|---|
| Source Serif 4 | `SourceSerif4-Regular.ttf.woff2` | `0263fc304226d90e224e53053855ad138303b70b` | *computed at fetch time — re-run contract* |
| Source Serif 4 | `SourceSerif4-Semibold.ttf.woff2` | `dd55f4e95ec9c29fb566d8617104afca31f0eeef` | *computed at fetch time — re-run contract* |
| iA Writer Quattro | `iAWriterQuattroS-Regular.woff2` | `a25cdbcdd3f2127e7c2f6d0fe2832a83ae2fc6e5` | *computed at fetch time — re-run contract* |
| iA Writer Quattro | `iAWriterQuattroS-Bold.woff2` | `d4c3f631f473d67dda90083bab4edd696b27b484` | *computed at fetch time — re-run contract* |

On the documented re-run the fetched bytes' SHA-256 is recorded into
`MANIFEST.json` `families[*].files[*].sha256`, and `tests/presentation_roundtrip.py`
recomputes it and compares — the recorded value and the on-disk bytes can
never drift apart.

### 3. woff2 file sizes (published GitHub metadata)

| Family | File | Size (bytes) |
|---|---|---|
| Source Serif 4 | `SourceSerif4-Regular.ttf.woff2` | 76,260 |
| Source Serif 4 | `SourceSerif4-Semibold.ttf.woff2` | 80,732 |
| iA Writer Quattro | `iAWriterQuattroS-Regular.woff2` | 44,416 |
| iA Writer Quattro | `iAWriterQuattroS-Bold.woff2` | 45,252 |

(Source Serif 4 archive asset `source-serif-4.005_WOFF2.zip` is 11,623,196
bytes; the two weights are read from `WOFF2/TTF/` at tag `4.005R`.)

### 4. ClearType render check (recorded human-verify item at phase end)

The 18px rendering of both faces must be verified on **Windows ClearType at
375px and 1280px** before the phase is signed off — the same two viewport
widths the UI-SPEC Registry Safety row names. Recorded here as a human
verify item, **not** claimed as done by this executor. Note the upstream
warning attached to `4.005R`: Windows has a CFF2-variable-font bug that can
corrupt text — we ship the **TTF-instance** woff2 files (`WOFF2/TTF/`), which
the release notes explicitly recommend for Windows, and we render at a fixed
weight pair (400/600 for Source Serif 4; 400/700 for iA Writer Quattro), so
no variable-font instancing runs in the browser.

---

## Fetch disposition

This executor shell has **no command execution and no byte-preserving fetch
path** (`web_fetch` returns text only, which cannot reproduce a woff2
byte-for-byte). Therefore **no byte was fetched** and the four files above are
**deferred**. Per the plan: the fallback decision stands (no vendor CSS
stack — `--font-paper` → Georgia, `--font-ledger` → `ui-monospace`, and every
UI-SPEC rule still holds), no UI-SPEC rule is withdrawn, and the vendoring is
a documented re-run:

1. Fetch the four pinned raw URLs from `MANIFEST.json` `families[*].files[*].url`
   (all `raw.githubusercontent.com` at the pinned refs above) with `curl -L`.
2. Place the bytes at `fonts/<family>/<file>` exactly as named.
3. Compute `sha256sum` per file into `MANIFEST.json` `sha256`.
4. Set `MANIFEST.json` `fetch.status` to `"shipped"` and clear `rerun`.
5. Re-run `python tests/presentation_roundtrip.py` — the sha256 rows are then
   verified against the on-disk bytes, and the `@font-face` srcs resolve.
6. Perform the ClearType render check (precondition 4) and mark it done in
   this file.
