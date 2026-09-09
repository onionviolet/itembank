# Interactive lesson trial

Link one, 2026-09-08. Runnable prototype, not production integration or accepted learner content.

## Run

From the repository root:

```sh
python3 -m http.server 8766 --bind 127.0.0.1 --directory prototypes/competition
```

Open `http://127.0.0.1:8766/interactive-lesson/`. The server exposes the synthetic competition subtree on loopback only. The existing `../rainfall.txt` is linked and quoted unchanged. No install, build, provider, account, or model is required. `lesson.md` carries the complete static explanation and table.

## Concrete LiaScript trial

The exact original input is `liascript-trial.md`. Its two `{{n}}` progressive blocks contain no imported template, executable script, quiz, or narration directive.

Used the official [LiveEditor](https://liascript.github.io/LiveEditor/) in its displayed offline editing mode. Created a blank project, pasted the input, and compiled it. The preview showed the source and objective. Next moved to the comparison page at `0/2`. Enter on the focused Next button showed step 1 at `1/2`. Enter again showed the subtraction at `2/2`. Reload retained the editor text. This establishes a compiled, keyboard-controlled progressive explanation, not offline packaging or recovered learner progress.

The browser-local project is `https://liascript.github.io/LiveEditor/?/edit/4EmDwTGZegb4Sb87yqVa9sB5`. It is not a published or portable course link. Reproduce by pasting the saved Markdown in a new project.

Primary documentation inspected: [official compendium](https://raw.githubusercontent.com/LiaScript/docs/master/README.md), metadata version 34.0.5, and [runtime license](https://raw.githubusercontent.com/LiaScript/LiaScript/master/LICENSE), BSD-3-Clause. Documentation describes Markdown extensions and progressive blocks. Those claims are distinct from the narrow observed trial. The hosted runtime was not pinned or installed locally, so exact hosted-version reproducibility is unproved.

## Pattern and licensing

LiaScript contributed portable text with learner-controlled progressive explanation. This prototype uses original native HTML details rather than its runtime, parser, quiz engine, or persistence. OpenMAIC's previously observed adjustable Taylor diagram contributed the parameter-control pattern. Its renderer brings React, Motion, and Tailwind dependencies, which this fixed comparison does not require. DeepTutor's grounding work informs keeping an unchanged, locatable source. This slice does not call or copy its implementation.

All new code and synthetic text are original. No third-party code or asset was copied and no dependency added. There is no new vendored license or dependency pin. Existing DeepTutor Apache-2.0 notices and OpenMAIC generation 0.3.6 pins remain untouched. Pin and review exact components and dependencies before later runtime reuse.

## Executed checks

| Check | Result |
| --- | --- |
| `node --test prototypes/competition/interactive-lesson/test.mjs` | 4 tests passed. All 25 allowed values, invalid input, reset and pageshow. Minimal DOM host has no provider or storage API. |
| `python3 prototypes/competition/interactive-lesson/test_static.py` | 4 tests passed. Exact source quote and SHA-256, local links, static fallback, CSP and contrast. |
| `python3 scripts/preflight.py --quick` | Exit 1 only on pre-existing `.agents/skills/author-bank/_attempts` mirror mismatch. All other executed gates passed. Full suites and clean-tree gate skipped by quick mode. |
| `curl --fail --silent http://127.0.0.1:8766/rainfall.txt` | Returned the unchanged synthetic source. |
| Preservation and diff review | `preservation-check.json` records no unexpected changes among 41 baseline files. Only the two authorized owner documents changed. `git diff --check` passed. Reviewed the new HTML/CSS/JS, browser artifact and owner additions. No production module was changed. |
| Browser keyboard | ArrowLeft changed 18 to 17 and difference to +5. Home plus increment produced 1 and -11. Enter opened a disclosure. Enter on reset restored 18 and closed it. End followed by reload restored 18. |
| Network | CDP capture across slider, button and reveal interactions returned zero request events, with no truncated events. CSP also denies connections and forms. |
| Reduced motion | Emulated preference matched. All sampled bars, buttons and details had animation `none` and transition `0s`. Override removed. Default also has no animation. |
| No JavaScript | Disabled script execution and reloaded. Source diagram, text, table and origin labels stayed visible. Dead controls were absent. Native disclosure still opened. JavaScript restored afterward. |
| Contrast | Ink `#18332d` on yellow `#ffe66b`: 10.83:1. On mint `#b7f3c3`: 10.72:1. Bold labels, numbers and signed text retain meaning without color. |
| Narrow layout | Screenshot inspected at 390 by 844. Scroll width 390. All six control targets at least 44 CSS pixels high. Viewport restored. |
| Touch and screen reader | Actual touch untested. In-app browser rejected `Input.dispatchTouchEvent` as unsupported. Touch override removed. Accessible names, range values, diagram description, details state and status text appeared in AX tree. No human screen-reader or announcement certification. |

The unchanged quote is visible in the page. Raw-source link activation did not produce a stable in-app document preview. Local HTTP retrieval and file integrity verify its target, not a claimed browser text-preview pass.

## Authority, recovery and limits

One builder, configured model, no subagents. Reads: repository, requested skills, public LiaScript docs. Writes: this subtree, absorption owner and chain packet. `baseline.json` records 41 pre-existing dirty or untracked hashes. Interaction creates disposable DOM state only, with no scores, learner evidence, accepted revisions, annotations, or reading-completion claims. Reset and pageshow restore source values and close disclosures.

Undo this link by removing its new subtree and reverting only its owner/packet additions. Preserve all pre-existing competition prototypes and concurrent files. No real learner file, commit, or push was involved.

Production sampling: `_inline`, `_callout_html`, `_render_blocks`, `_static_instructional_html`, `guided_stages`, `_stage_html`, and capability profiles. Large modules were not read exhaustively or changed. Vision sampling covered source-to-course, portable content, visual ambition, external readers and the September 8 competitor clarifications. This is not a whole-vision audit.

Human aesthetics, physical touch and screen-reader review remain owed. Production integration, canonical source binding, accepted-revision recovery, live generation quality and clean-machine restore are unproved. Reading R1 through R3, Phase 20 human checks and parity backend debt retain their existing owners.
