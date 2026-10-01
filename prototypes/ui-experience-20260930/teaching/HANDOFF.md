# Teaching lane handoff

Status: READY for prototype comparison and bounded integration.
Date: 2026-09-30. Ownership: only this teaching folder.

## Deliverable and design

The runnable `index.html` uses an original finite distance/time lesson. Mira
walks at 3 m/s and Noor at 5 m/s from a common start. A learner keeps a first
prediction about the gap at 6 seconds, reveals the public model, then changes
the clock. The track, exact distances, gap, distance/time graph, and three
worked equations update together. Replay has pause and reset; reduced motion
reaches the final state immediately. Worked-step controls emphasize the
corresponding walker. This is synthetic exploration, never an assessment.

The composition gives the experiment most of the width, with the retained
prediction beside it, then a worked explanation and a separate private-note
ground. Blue means Mira; orange means Noor. The gap uses neutral emphasis.
Notes and feedback use different semantic roles. Narrow layouts stack the
same material. Light and dark modes remain deliberate and independently
selectable. No remote fonts, assets, frameworks, or scripts are loaded.

Reference R1 opens a focused explanation of units and model assumptions.
The practice detour changes time to 4 seconds and compares a public demo
prediction with the worked result. Both detours preserve clock, prediction,
expanded step, note, and return focus. A synthetic note uses browser storage
with acknowledged save, reload restoration, and an explicit failure notice.
Prediction and clock reset on reload; this is disclosed below.

## Files and running

| File | Purpose |
| --- | --- |
| `index.html` | Runnable original synthetic lesson and useful script-free state |
| `teaching.css` | Responsive light/dark composition and subject visuals |
| `teaching.js` | One finite model, linked updates, prediction and detours |
| `lesson.md` | Plain Markdown core meaning, assumptions, worked steps, table and transfer |
| `inspect.mjs` | Focused disposable browser inspection, not a repository test suite |
| `observed/` | Actual screenshots and `inspection.json` observations |

Serve from the repository root:

```sh
python3 -m http.server 8798 --bind 127.0.0.1 --directory prototypes/ui-experience-20260930/teaching
```

Open `http://127.0.0.1:8798/` or add `?theme=dark`.
Opening the HTML file directly also works, subject to browser file-origin
storage policy. Inspection used its own temporary loopback server.

The actual inspection invocation was `node prototypes/ui-experience-20260930/teaching/inspect.mjs`
with `ITEMBANK_PLAYWRIGHT_MODULE` pointed at the existing local Playwright
installation and `ITEMBANK_CHROMIUM` pointed at installed Chrome. Neither was
installed or changed. The script accepts those environment variables; use
the integration chat's already established browser paths. Re-run after
adapting the prototype to refresh screenshots.

## Actual preview evidence

Chrome rendered 1440 × 1000, 390 × 1000, and 320 × 1000 viewport sizes in
light and dark, with full-page screenshots of prediction, reveal with graph,
and reference. `observed/inspection.json` records the measurements and journey.

The full synthetic journey passed in each size/theme pair: prediction 10 m,
reveal 12 m at 6 s, keyboard ArrowRight to 7 s (21 m, 35 m, 14 m gap), minus
back to 6 s, expanded Mira step, note save, reference Escape return, practice
prediction 8 m, and return to the same clock and note. Reload restored the
browser-local synthetic note. Reference and practice returned focus to their
launch buttons. All visible button heights were at least 44 px. Document
overflow was zero; no page errors occurred.

A JavaScript-disabled 390 px render retained the worked explanation, table,
and full core meaning with inactive controls hidden. An injected storage
failure showed an honest unsaved notice. Normal-motion replay/pause preserved
the stopped clock; reduced-motion replay reached 6 s immediately.

Visually inspected `observed/light-1440-reveal.png` and
`observed/dark-390-reveal.png` in the image viewer. The first rendering showed
phone diagram labels and inline retained-prediction values were too small or
crowded; the narrow CSS now increases diagram label/marker sizes and aligns
prediction/result as two clean rows. Final screenshot files were regenerated
after that adjustment. This is rendered inspection, not human preference,
accessibility certification, or learning-efficacy evidence.

## Inspiration and authority

Read the shared parallel packet, the September 30 UI goal/donor addition,
the September 25 interaction craft and synthesis, the September 18 teaching
report, relevant September 8/30 vision entries, and Source-to-Course's lesson
presentation, progressive enhancement and tracer requirements. Sampled the
existing `render_lineplot` implementation in `surfaces/lesson_interaction.py`.
Did not read whole parser/runtime modules or perform an exhaustive vision audit.

Refreshed [Brilliant's official Solving Equations article](https://blog.brilliant.org/solving-equations/)
on September 30. The November 8, 2024 article describes concrete puzzles,
manipulation before formal naming, and introducing theory after action.
This prototype transfers that sequence into original material. It does not
copy Brilliant assets or claim product parity, private-course observation,
or demonstrated learning gains. The shared research already supplies the
broader primary-source interaction rationale.

## Integration instructions and gaps

Adopt the state mechanism and interaction sequence independently of this
prototype's shell. Keep one `time` value feeding track coordinates, numerical
readouts, graph cursor and equations. Prediction is a retained first value
about a fixed 6-second target; changing the clock must not rewrite it. Keep
the model's assumed common start, same direction and constant speeds visible.

Existing bounded renderer code supports line models, static meaning and
prediction already. Production should extend that renderer only through its
current validated finite-capability contract. A generic distance/time scene,
new teaching grammar, generated scripts, or durable demo prediction format
is not approved by this folder. Inspect current parser validation and exact
format owners before production integration. Do not paste this model into an
assessment surface or introduce a second scorer. Assessment keyed content
continues to require runtime disclosure; demo feedback remains clearly public.

Use existing production note ownership, revision and recovery rather than
the prototype localStorage key. The synthetic key here has no course/source
identity and no export, conflict or cross-device recovery contract. The note
is the only draft restored on reload. Prediction, clock and expanded steps
are in-memory demonstration state; do not imply durable recovery for them.
The save debounce has a small pending window before storage acknowledgement.

Keyboard, overflow, reduced motion, dialog return, and JS-disabled meaning
were checked. Real touch, screen readers, zoom/reflow at 200 percent, contrast
ratios, assistive-technology announcements and human acceptance remain open.
Usefulness and user preference are unverified. No full preflight, commit,
push, package/app build, installation, or release ran. Recovery removes only
this teaching folder after preserving any desired prototype evidence.
