# Decision packet: the 17A-04 browser harness supply-chain approval

Drafted 2026-08-25 by the orchestrating session so that 17A-04 Task 1 can
start the moment Weibao decides. Nothing is installed and nothing is pinned
until he does. This packet is the section 3 adoption argument
`SUPPLY-CHAIN-POLICY.md` requires, plus the two items only he can settle.

## What is being asked

Approve a dev-only, exactly pinned Playwright harness for
`tools/visual_qa.py`, under policy section 2.5 (build and CI tool, fetched at
install time, pinned to an exact version, recorded in `VENDORED.md`). It
never ships in the runtime, and `17A-04-PLAN.md` out_of_scope already forbids
shipping it.

## The section 3 gate, argued

- **Capability that earns it:** real layout at 1280, 768, and 375; 200
  percent zoom and reflow; visible focus order; 44px target measurement;
  contrast in light, dark, and oled; reduced motion. Gates 4, 5, 10, 11 of
  the visual QA matrix need a layout engine.
- **Alternative considered, with measured cost:** jsdom 29.1.1 is already
  pinned and in CI, and it does no layout (STATE.md line 845 records this as
  the exact reason D-09 exists). Hand verification by Weibao for every
  template change is the no-dependency alternative; its cost is his time on
  every 17A/17B iteration, which is the cost this harness removes.
- **Size and transitive surface:** the Python `playwright` wheel plus a
  Chromium build and an ffmpeg build fetched by `playwright install`;
  hundreds of megabytes cached outside the tree, zero runtime imports.
- **Maintenance signal:** Microsoft-maintained, releases monthly, pinned
  exactly so drift is a deliberate bump.
- **Removal path and degraded behavior:** delete the `VENDORED.md` row,
  `tools/visual_qa.py` refuses to run with a one-line message, and the QA
  matrix falls back to human review; nothing in the runtime notices.

## The two calls only Weibao can make

1. **The ffmpeg component is LGPL.** Policy section 2.4 routes copyleft to
   an explicit decision. It is dev-only and never redistributed, which is the
   easiest LGPL case, but the policy does not carve that out on its own.
   Option A (recommended): approve with the note that dev-only, non-shipped
   LGPL tools are acceptable. Option B: `playwright install chromium
   --no-shell` style installs that skip ffmpeg entirely if video capture is
   not needed; the harness takes screenshots, not video, so this is viable.
2. **Which pin.** Recommended: the latest stable `playwright` Python release
   at decision time, recorded with SHA-256 in `VENDORED.md` (which this plan
   would create, backfilling the KaTeX and CodeMirror rows section 2.2 owes).

## What happens on yes

17A-04 Task 1 executes: `VENDORED.md` created with the three rows, the pinned
install, `tools/visual_qa.py` and the extended
`tests/visual_accessibility_roundtrip.py`, evidence into `17A-QA.md`. Task 2
remains his human A11Y-01 review either way.

## What happens on no

17A-04's QA matrix is produced by hand: Weibao performs the scripted review
in `17A-04-PLAN.md` Task 2 directly, and the freeze records that the harness
was declined with this packet as the reconsideration record.
