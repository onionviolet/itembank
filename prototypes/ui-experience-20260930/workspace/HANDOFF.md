# Workspace lane W

Status: **READY for integration review**, 2026-09-30. Prototype source and local
browser evidence only. Production, installed-app, human preference and
representative accessibility acceptance remain unverified.

## Result and design

The prototype puts a measured reading column beside one companion pane, switching
between source reference and private note. The paper surface, strong prose
hierarchy, blue controls, cyan source excerpt and violet note anchor distinguish
content roles. A concept map would not help this small task, so none was added.
The same synthetic two-walker task includes time manipulation, a prediction,
worked explanation, passage actions, note save and exact return controls.

Obsidian inspiration is spatial arrangement, rather than a canvas. Its official
[Tabs documentation](https://obsidian.md/help/tabs), checked 2026-09-30, describes
split tab groups and resizing their edges. This prototype transfers that idea
to a bounded reading/companion pair and adds left/right-arrow resizing. No donor
code, assets or persistence model were copied. Existing goal, craft synthesis,
overhaul W record and workspace absorption report were read before implementation.

## Owned files and preview

| File | Purpose |
| --- | --- |
| `index.html` | Semantic synthetic task and reading/reference/note composition |
| `workspace.css` | Reusable visual roles, grid, divider, focus and narrow layouts |
| `workspace.js` | Presentation actions and explicitly prototype-only storage |
| `preview.py` | Bounded reproducible rendering and journey probes |
| `evidence/` | Sixteen screenshots plus measured `preview.json` |

From repository root, serve with:

```sh
python3 -m http.server 8843 --bind 127.0.0.1 --directory prototypes/ui-experience-20260930/workspace
```

Preview: `http://127.0.0.1:8843/`, dark: `http://127.0.0.1:8843/?theme=dark`.
The lane preview server remains live for integration review. It serves only this
owned folder. Re-run browser evidence with:

```sh
python3 prototypes/ui-experience-20260930/workspace/preview.py
node --check prototypes/ui-experience-20260930/workspace/workspace.js
```

No full preflight, package/app build, install, release, commit or push ran.
All writes are confined to this owned folder. Remove only this folder to undo
the prototype. The browser demo key is `itembank-workspace-demo-v1`; deleting
that key clears only this demo's saved note.

## Actual preview evidence

Chrome headless rendered 1440 × 1000 desktop and 390 × 844 narrow views in light
and dark. Each performed reading, elapsed-time adjustment, note, save, source
reference, return, prediction/reveal, return, reload, and injected save failure.
Screenshots show reading, note, reference and prediction in each configuration.
All four journeys passed with no page errors or page-level horizontal overflow.

Observed checks: desktop divider responds to pointer drag and keyboard arrows;
slider at eight seconds describes 24 m, 40 m and a 16 m gap; source/note return
restores the originating passage action's focus; prediction return restores its
originating button; prediction input survives a detour; saved note survives a
reload; failed save keeps the current draft. Extra 320px and 768px probes check
overflow and keyboard slider operation. A 390px JavaScript-disabled probe checks
the static distance explanation and visible correctly proportioned bars.

Visually inspected screenshots: `1440-light-reading.png`,
`1440-dark-note.png`, `390-light-note.png`, `390-dark-reading.png`.
Other screenshots were captured, not all visually reviewed individually.

Useful comparison inputs:

- `evidence/1440-light-reading.png`: reading and source split.
- `evidence/1440-dark-note.png`: reading with saved private note and changed time.
- `evidence/390-light-note.png`: narrow note destination and return control.
- `evidence/390-dark-reading.png`: narrow reading and reachable passage actions.
- `evidence/preview.json`: exact dimensions and bounded results.

## Integration into the existing reading desk

I1: Reuse grid ratio, divider, companion treatment, 44px controls and focus
composition from CSS. Prefix selectors and map tokens to the shared theme;
do not paste global body, button or heading styling into production. Keep the
existing shell, source role and private-note role. A resize preference is a
disposable presentation value, not course content or a new durable object.

I2: Add only presentation handlers around existing `#source-content`, `#note`
and `#save-note`. Passage-to-note should focus the existing draft and expose its
context without auto-saving or overwriting wording. If quoting selection is
added, require an explicit append action and keep it in draft only. The current
source-range note model does not accept this prototype's passage anchor as a
durable locator. Show an ephemeral selection cue or label the whole source range;
do not invent a persistent passage-note identity.

I3: Reuse `save_reading_note`, expected notes fingerprint, source availability,
stale-source recovery, in-flight draft protection and existing read declaration
unchanged. Never transfer the prototype's `localStorage`, demo save status or
single-note overwrite into production. Existing production notes are shared
across assignments using the source, while this synthetic note is only a demo.

I4: Reference disclosure may present the already available source locator,
occurrence and revision data. It must not fabricate an excerpt, confidence,
source binding or rights. The current production source view is itself a reading
range, so a duplicated reference excerpt is unnecessary unless a real separate
reference target exists. Preserve current unavailable and stale states.

I5: Narrow composition uses one destination at a time, same DOM order and visible
Reading/Reference/My note buttons. Adopt only after testing hidden destinations,
focus return, notes failure/retry, exact source revision and existing draft
recovery. Keep a usable stacked no-script fallback. Preserve production
`rememberReading`/`restoreReading` instead of replacing them with demo return
state. Names sampled in `surfaces/reading_desk.py`: CSS, SCRIPT and render body;
the file's relevant windows were read, not the larger daemon or lesson modules.

## Limits and operational notes

This is one deliberate workspace composition, not a whole-product visual
comparison. Companion tabs do not implement arbitrary draggable tab groups.
Passage actions target one complete synthetic paragraph; highlight is visit-only.
Saved note replaces one browser demo value; unsaved draft, resize, selected tab,
time and prediction are visit-only. There is no source-change conflict, offline
restore, course-note journal, real assessment, score or completion operation.
No real bank, learner file or coursework was accessed.

Physical touch, human screen reader, 200% zoom, high contrast and learned benefit
were not verified. Minimum 44px controls and native keyboard operations are
implemented but do not certify accessibility. Native/browser Back is not the
demo's detour control; exact return uses the explicit buttons. On narrow screens,
the view tabs switch presentation; the explicit return buttons restore passage
focus and position. Desktop companion content follows the natural document
scroll, so exceptionally long readings may benefit from a bounded sticky pane.

Operational finding: local Python already has Playwright; headless Chrome works
for this synthetic preview without changing browser extensions or the installed
app. Save-failure injection must use an evaluate wrapper function, since an
assigned function returned by evaluate can be invoked by Playwright. The initial
probe failed at that injection; the repaired complete probe passed. Evidence
files reflect the successful final run.
