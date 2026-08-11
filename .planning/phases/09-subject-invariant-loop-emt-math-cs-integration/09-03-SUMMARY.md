---
phase: 09-subject-invariant-loop-emt-math-cs-integration
plan: 03
subsystem: supply-chain
tags: [katex, human-gate, pending-approval, vendoring]

status: PENDING-HUMAN-APPROVAL
approved: false
resume_signal: "approved katex=0.18.4" (+ 09-04 computes/records the tarball SHA-256 after verifying the published integrity below)

provides:
  - Fully researched immutable KaTeX approval candidate (metadata only; zero bytes downloaded, zero repository changes)
  - The exact version/integrity/license/source/inventory 09-04 must fetch and independently verify
blocks: [09-04 vendoring, 09-05 Math fixture row]

verification:
  - command: "python -c \"from pathlib import Path; s=Path('.planning/phases/09-subject-invariant-loop-emt-math-cs-integration/09-RESEARCH.md').read_text(encoding='utf-8'); assert 'Package Legitimacy Audit' in s and 'katex' in s.lower() and 'SUS' in s\""
    exit: 0
    notes: "The 09-03 automated audit guard passes (research audit text present)."
  - "Human gate: NOT yet approved. The ask tool returned no interactive answer in this autonomous run; per the plan this checkpoint is never auto-approved, so 09-04 must not fetch or vendor any bytes until a human replies with the resume signal."

human-check:
  - "Official ownership: github.com/KaTeX/KaTeX; npm package katex; maintainers incl. edemaine (MIT) and khanacademy. VERIFIED via registry payload."
  - "Immutable release: tag v0.18.4; git tree sha 49dc3d986747fd7d3bb25b597bcb98b071ae6035 (matches npm gitHead). VERIFIED via GitHub API."
  - "License: MIT (npm 'license': 'MIT'; LICENSE file present in the tag tree). VERIFIED."
  - "Published tarball integrity: sha512-IMPntbRLOU+eu88XDiFKqQ8Akhr9Tv7jDMXqPhjG9SI1JMA4DIgXk4x9k4skJz2NZJXBRbC+2pYBLj9olqcZow== ; shasum aa09d0bfbcbab71a9a0f9d420def6c0d0a227a94. npm publishes sha512/sha1 only; the SHA-256 is computed and recorded by 09-04 after verifying this integrity (the resume signal's sha256 field is therefore filled at fetch time)."
  - "Distribution inventory (to verify byte-for-byte at fetch): dist/katex.min.css, dist/katex.min.js, dist/contrib/auto-render.min.js, dist/fonts/* (all CSS-referenced), LICENSE. Tarball fileCount 213, unpackedSize ~4.0 MB."
  - "No archive/package byte downloaded, no vendor/cache/staging/repository/package-manifest change made by this checkpoint."

key-decisions:
  - "Candidate version pinned: katex 0.18.4 (current npm latest at research time 2026-08-08, flagged [SUS] on recency only by the Package Legitimacy Audit; trusted upstream + 21M downloads/week)."
  - "Because npm publishes sha512 integrity (not sha256), the approval record binds the sha512 integrity; 09-04 verifies the fetched tarball against it and records the computed SHA-256 in 09-04-SUMMARY.md, satisfying the plan's 'verified 64-hex' requirement with a stronger published checksum."

duration: 20min
completed: 2026-08-11
---

# Phase 9 Plan 03: KaTeX Supply-Chain Gate — PENDING HUMAN APPROVAL

**Blocking metadata-only verification of the exact KaTeX release to vendor. Research complete; approval NOT yet granted.**

## What was verified (inspect-only, no download)
- The npm registry payload for `katex@0.18.4`: MIT license, `github.com/KaTeX/KaTeX` repository, `dist` tarball URL `https://registry.npmjs.org/katex/-/katex-0.18.4.tgz`, integrity `sha512-IMPntbRLOU+eu88XDiFKqQ8Akhr9Tv7jDMXqPhjG9SI1JMA4DIgXk4x9k4skJz2NZJXBRbC+2pYBLj9olqcZow==`, shasum `aa09d0bfbcbab71a9a0f9d420def6c0d0a227a94`, fileCount 213, unpackedSize ~4.0 MB.
- The immutable GitHub tag `v0.18.4` tree (sha `49dc3d986747fd7d3bb25b597bcb98b071ae6035`, matching npm's `gitHead`): LICENSE present; the release carries the browser `dist/` and `contrib/` trees.

## State
- **The human gate is OPEN.** The `ask` tool returned no interactive answer in this autonomous run; per 09-03-PLAN.md this checkpoint is **never auto-approved**. 09-04 must not fetch, verify-bytes, or vendor anything until a human replies `approved katex=0.18.4` (or names a different version) with the sha256 filled at fetch time after integrity verification.
- The automated 09-03 audit guard passes against 09-RESEARCH.md.

## Next action when approved
Reply with the resume signal; 09-04 then downloads the single immutable tarball into a temp dir, verifies sha512 integrity + shasum, computes and records the SHA-256, inventories `katex.min.css` / `katex.min.js` / `contrib/auto-render.min.js` / `fonts/` / `LICENSE`, and vendors them under `vendor/katex/`.
