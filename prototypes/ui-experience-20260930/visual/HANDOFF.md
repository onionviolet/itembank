# Visual lane handoff

Status: **READY for integration comparison**, 2026-09-30.
Owned writes: this folder only. No production source, other lane, shared planning,
commit, push, build, installation or learner material was changed.

## Open the comparison

Run from the repository root:

```sh
python3 prototypes/ui-experience-20260930/visual/preview.py --port 8808
```

Open `http://127.0.0.1:8808/comparison.html`. The loopback preview was left
running on port 8808 for the integration chat. It is disposable and has no
production service dependency. The browser panel open request returned queued,
so a visible user visit is not claimed.

`index.html?composition=atlas&theme=light` and
`index.html?composition=studio&theme=dark` choose candidates directly.
The in-page composition and appearance switches preserve time, prediction,
private draft, practice draft and revealed explanation within the open page.
Reloading drops those drafts. The UI states this limitation.

## Same-content rendered comparison

Both complete candidates use exactly one HTML lesson and one demonstration
script: walkers at 3 and 5 m/s, shared elapsed time, prediction at 12 seconds,
source reference, private note and practice at 8 seconds. Everything is fictional
and unscored. Neither candidate provides real assessment feedback.

| Code | Composition | Observed character and tradeoff |
| --- | --- | --- |
| D1 | A, Field Atlas | Serif section entry, warm field, open prose, fine rules, human walker marks, illustrated exploration and a separate source gutter. Reading, diagram and source are simultaneously visible on desktop. The diagram is smaller and the lower left has more open space. Best candidate for a reading-led activity. |
| D2 | B, Motion Studio | Compact tool-voice section entry, cool field, wide instrument canvas, grid and position markers, elapsed-time/readout dock, prediction beside the experiment. The diagram becomes the active object. Source and reading sit below it. Better candidate for this manipulative task, based on this designer's judgment, not a user preference result. |
| F1 | Current source baseline | Fresh `presentation.surface_shell` and `theme.theme_css` on the same lesson. The stock stacked composition puts reading above the experiment and source/note together farther down. Minimal CSS supplies the diagram and intrinsic control layout because the new fictional content needs those primitives. This is a static source-shell comparison, not a live served course or an exact preexisting lesson renderer. |

The baseline uses actual current source and records its hashes in
`baseline-source-hashes.json`. `source-baseline-light.html` and
`source-baseline-dark.html` contain all the same lesson tasks; practice controls
are disabled because these are static visual references. The separate
`baseline.css` switch option is only an approximate same-content workshop
projection. Prefer the source-generated baseline in the comparison gallery.

The earlier actual workshop preview was also captured as
`observed/current-original-1440.png`. Its garden task differs, so it is useful
for shell context only and is not the controlled same-content comparison.

## Files and actual preview evidence

| File group | Purpose |
| --- | --- |
| `index.html`, `design.css`, `demo.js` | Both complete interactive candidates, same semantic content and state |
| `comparison.html`, `baseline.css` | Side-by-side screenshot gallery and approximate baseline switch |
| `render_source_baseline.py`, `source-baseline-*.html`, `baseline-source-hashes.json` | Fresh current-source shell reference and generation provenance |
| `preview.py`, `inspect.mjs` | Loopback font-aware preview and bounded rendered inspection |
| `observed/`, `manifest.json`, `OPERATIONS.md`, `HANDOFF.md` | Screenshots, browser observations, owned-file integrity and handoff |

Actual commands:

```sh
python3 prototypes/ui-experience-20260930/visual/render_source_baseline.py
node prototypes/ui-experience-20260930/visual/inspect.mjs
python3 prototypes/ui-experience-20260930/visual/preview.py --port 8808
```

The existing temporary Playwright installation and installed Chrome were used
only for the preview harness. No dependency was added to the product. The
inspection script imports that temporary Playwright path; another machine must
change the import and Chrome executable, or use its own browser to inspect the
HTML. Font files are read from the existing repository assets, not downloaded.

Final captures: A, B and the approximate baseline each at 1440 × 1000 and
390 × 1000 viewports in light/dark, 12 full-page captures. The fresh source
baseline adds four captures at those same widths and themes. Additional
captures show 12-second Studio, the practice dialog, no-script Atlas, and the
earlier workshop. Screenshot heights differ because the full page is captured.
`observed/metrics.json` stores the actual metrics for the 12 candidate/projection
renders, not an invented general accessibility result.

Viewed as images: Atlas light desktop, Atlas light narrow, Atlas dark narrow,
Studio light desktop, Studio dark narrow, current-original desktop, current
source-baseline light desktop and Studio practice dialog. Inspection found and
fixed an awkward Studio title gap, excessive reading-row stretching and small
diagram labels. Studio uses position dots rather than the Atlas walker figure.

Focused browser checks actually passed: zero horizontal overflow at 1440/390;
44px-or-larger visible target heights; correct 8-second and 12-second readouts;
range control by arrow key with visible focus; reduced-motion removes walker
transitions; source/static meaning readable without script; no page errors;
private/practice drafts retained on detour return and composition switch.
The final harness prints PASS. No full preflight or product test expansion ran.

## Primary reference and contract sampling

Read AGENTS.md, the dispatch packet, AGENT-WORKFLOW section 1, USER-VISION's
September 30 statements, SOURCE-TO-COURSE learner-experience sections,
UI-SPEC sections 7 and 15.3, the UI goal owner's September 30 section, earlier
visual-overhaul evidence and September 25 PRODUCT-CRAFT research.
Production shell entry points and existing visual preview test were sampled;
large runtime, parser, scoring and evidence modules were not read or audited.

[Linear's March 2026 refresh](https://linear.app/now/behind-the-latest-design-refresh)
was opened and checked September 30. Its team documents dimmer navigation,
compact tabs, softer separators and in-app old/new comparison and palette
iteration. Transfer here: restrained navigation plus a same-state comparison
switch. This is an original learning composition, not copied Linear identity,
assets or code. A and B intentionally differ beyond accent color.

## Integration instructions and limits

A1: Use the live comparison and full-size gallery before selecting. My provisional
recommendation for the motion task is Studio's wide experiment and adjacent
prediction, with Atlas available as a reading-led composition. Keep the actual
production global destinations; this demo's local Learn/Practice/Sources/Notes
links are lesson-local navigation, not a proposed route replacement.

A2: Port composition rules into existing presentation primitives and palette
owners after I's ownership/fingerprint check. Prototype palettes are isolated
experiments; do not copy them into a second production theme authority. Paper,
Ledger and Chrome roles use existing vendored voice assets. The decorative Atlas
chapter mark is not an evidence count. Keep source, note and assessment roles
separate and the existing runtime/disclosure contracts unchanged.

A3: Prefer T's teaching implementation and W's workspace behavior where they
pass the same journey. This lane's range, feedback and dialog demonstrate
presentation only. No session format, accepted artifact, source grant,
canonical note persistence or assessment adapter is introduced here.

R1: Human visual preference, screen-reader equivalence, high-contrast review,
color contrast certification, 200% zoom, touch-device behavior and installed
acceptance remain open. The DOM follows read/explore/predict; Studio's desktop
visual staging puts exploration first. A reader can still navigate the explicit
lesson sequence, but that staging difference deserves a human walkthrough.
These full-page prototypes are long on narrow screens. No learning-benefit or
complete-product-parity claim follows from the screenshots or browser checks.

R2: No-script Atlas retains the six-second example and twelve-second derivation;
interactive buttons require script. A and B keep only in-page drafts. The
integration lane must use existing recovery/persistence instead of treating
this demo as a note store. The static baseline is intentionally not interactive.

Recovery: stop the disposable preview process and remove only this folder's
reviewed files. All files were newly created under an initially absent owned
folder. Do not restore source hashes over anyone's newer production edits.

## User-directed refinement: condensation and direct interaction

September 30 follow-up: the user asked for more condensation, interaction and
intuitive behavior. Status remains READY for design integration comparison.
Only this lane's folder changed.

F2: Studio's collapsed initial full-page height changed from 1563 to 1240px at
1440px viewport width, and 2792 to 2136px at 390px. Those are approximately 21%
and 24% reductions. Measurements are PNG dimensions of actual full-page
captures at 1000px viewport height, not reading-efficiency claims. The diagram,
formula, speed readouts, prediction and source locator stay visible. Long
explanation, source excerpt and private note use native disclosures. Atlas
starts these disclosures expanded. Source/Notes links open their relevant
content. The private note summary distinguishes Empty from Draft.

F3: Added touch-sized Reset, 6 s and 12 s controls alongside the range. The
prediction action now says Compare at 12 seconds, updates the diagram and
readouts to 36/60 m, and reveals the unscored explanation. User drafts remain
in the page. This is still a prototype demonstration, not scoring or evidence.

R3: The compact starting state does not imply content was read or completed.
The note indicator means an unsaved in-page draft, never a saved note. Reload
still drops preview state. Choosing a time preset before predicting is allowed
because this is an open exploration, not an assessment. No autoplay was added.
Human discoverability and the amount of collapsed material remain open questions.

Re-ran the bounded inspect.mjs harness: PASS for the 12 light/dark desktop/narrow
renders, preset action, reveal-to-diagram link, draft retention, keyboard range,
44px target heights, no overflow, no-script meaning and reduced motion. Updated
images in observed/ now show this refinement. Explicitly viewed the new Studio
light desktop/narrow captures, also stored as *-condensed.png. The static source
baseline remains the original same-task source-shell reference; it does not
pretend to include the newly added interactive shortcuts. Updated manifest
hashes identify the final owned artifact set. No full product suite ran.

Integration should evaluate the condensed Studio as the latest B candidate.
Keep the prior recommendation provisional. Condensation is fewer simultaneous
choices and less default context, not smaller reading type or smaller targets.
