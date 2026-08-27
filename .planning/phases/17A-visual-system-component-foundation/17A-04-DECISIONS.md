# Phase 17A-04 decisions

## D-17A-04-1. The Playwright browser harness is approved, with ffmpeg

**Date:** 2026-08-27. **Approved by Weibao**, answering
`.planning/DECISIONS-17A04-DRIVER-2026-08-25.md`, which had been waiting since
2026-08-25.

**Question.** Approve a dev-only, exactly pinned Playwright browser harness for
`tools/visual_qa.py`, adopted under `SUPPLY-CHAIN-POLICY.md` section 2.5 (a
build or CI tool, fetched at install time rather than vendored, pinned to an
exact version, recorded in `VENDORED.md`), never shipped in the runtime?

**Recorded answer: approved, option A on the LGPL sub-call.** The harness is
adopted, and the LGPL ffmpeg component installs with it, with the note that
dev-only, non-shipped LGPL tools are acceptable. This sets a reusable precedent
for future dev-only LGPL tooling.

**What it buys.** Real layout at 1280, 768 and 375; 200 percent zoom and reflow;
visible focus order; 44px target measurement; and contrast in light, dark and
oled. Gates 4, 5, 10 and 11 of the visual QA matrix need a layout engine.
`jsdom` 29.1.1 is already pinned and in CI and does no layout, which is the
recorded reason D-09 exists.

**What the alternative cost.** Hand verification by Weibao on every template
change, on every 17A and 17B iteration. That is precisely the cost the harness
removes.

**Size and surface.** The Python `playwright` wheel plus a Chromium build and an
ffmpeg build fetched by `playwright install`: hundreds of megabytes cached
outside the tree, and **zero runtime imports**. Section 3.2's near-zero
transitive target is answered by the zero-runtime-import property rather than by
a package count. Microsoft-maintained, monthly releases, pinned exactly so any
drift is a deliberate bump.

**Removal path and degraded behavior.** Delete the `VENDORED.md` row;
`tools/visual_qa.py` refuses to run with a one-line message; the QA matrix falls
back to human review; nothing in the runtime notices.

**The pin.** The latest stable `playwright` Python release at decision time,
recorded with its SHA-256 in `VENDORED.md`. Not yet chosen: the executor
resolves and records the exact version.

**Option B, recorded as considered and not taken.** Installing so ffmpeg never
arrives would have avoided the LGPL artifact and set no precedent, at no
capability cost, since the harness takes screenshots rather than video. Weibao
chose to approve ffmpeg anyway.

**Consequence for `VENDORED.md`.** This file does not exist at the repository
root today. Either this plan or plan 14C-01 Task 2 creates it, whichever runs
first, and the other appends. It carries the KaTeX and CodeMirror backfill rows
that policy section 2.2 already owes. The two approvals given on 2026-08-27,
this one and `14C-DECISIONS.md` D-14C-3, are the same section 3 gate and produce
the same file.

**What proceeds.** 17A-04 Task 1 executes: `VENDORED.md` rows, the pinned
install, `tools/visual_qa.py`, the extension to
`tests/visual_accessibility_roundtrip.py`, and evidence written into
`17A-QA.md`.

**What this does not settle.** Task 2 remains Weibao's own human A11Y-01 review,
under either answer. An agent never self-certifies accessibility. The 17A freeze
also stays blocked until the Phase 13.9 walking skeleton has been walked, which
is a separate condition this approval does not touch.
