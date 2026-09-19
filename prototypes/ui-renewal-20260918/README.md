# Itembank UI renewal showcase

**Status: improved UI version, WIP and highly changeable.** The user recognizes
this as an improvement, not a final design or a frozen specification. Layouts,
visual styling, navigation, question workspaces, interactions and scope may be
revised or replaced as better evidence and needs emerge. Preserve useful
findings without treating this implementation as the default answer.

Future in-app code execution remains a supported product direction. Leave room
for a runner, output, test results and debugging beside the learner's code.
The current execution-unavailable state is a prototype limitation, not a ban
or a permanent UI constraint. Execution requires an isolated runner and draft
recovery. Runtime-owned grading remains distinct from execution output.
No execution implementation or production integration is claimed here.

Run from the repository root:

```sh
python3 -m http.server 8794 --bind 127.0.0.1 --directory prototypes/ui-renewal-20260918
```

Open <http://127.0.0.1:8794>. The static files also run by opening index.html.
No build, external font, network dependency, model call or account is needed.

## Delivered

One synthetic learner journey through study desk, course overview, interactive
lesson, three practice screens, retained feedback, explicit question advance,
session review and in-tab resume. Desktop and phone use different compositions.
Light and dark appearance share the new scoped presentation system. Competitor
inspiration is recorded in research/references.md with primary URLs and evidence
limits. BRIEF.md contains the original request and refined prompt.

## Verification on 2026-09-18

| Check | Observed result |
| --- | --- |
| Browser-rendered desktop | Desk, lesson and feedback screenshots inspected at 1280 by 720 |
| Application-sized browser | 1100 by 760, no page overflow and suspended practice resume visible |
| Phone browser | 390 by 844, desk, lesson and feedback checked with no page-level horizontal overflow |
| Keyboard exploration | ArrowRight changes time from 5 to 6 seconds and updates distance gap to 12 m |
| Practice sequence | Selected responses, previewed feedback, explicitly advanced through all three questions and reached review |
| Focus | Next question focuses the new question heading |
| Exploration reset | Reset restores 5 seconds and the 10 m gap |
| Course overview | Rendered and inspected at 1100 by 760 |
| Lesson detour | Return to question restores the existing selected response and feedback |
| Skip link regression | Activating it in practice preserves #practice and focuses main |
| Appearance | Dark feedback inspected at phone width |
| Syntax | node --check app.js passed |
| Repository quick preflight | All executed gates passed. Python suites, JS suite and clean-tree gate deliberately skipped by --quick |
| Vision audit | No missing dated interpretations, planning effects or inbox dispositions. Historical link and relationship backlog remains |

Browser interaction used the in-app browser after the standalone Playwright
connector failed to connect. Screenshots were inspected in the task, not saved
as a separate screenshot archive. Reduced motion is implemented in CSS but was
not exercised under an emulated OS preference. Static fallback wording is in
noscript but the browser was not run with JavaScript disabled. These are source
checks, not full accessibility acceptance.

## Boundaries and recovery

This is a presentation prototype, not an installed-app update. The fixed sample
explanations are deliberately labeled and are never a grading system. Nothing
is stored in localStorage or sent to the production daemon. Reload clears the
sample session. In-tab navigation retains it. Production needs authoritative
resume, submitting/error states, feedback permissions and evidence-driven review.

Real scoring, server persistence, every response format, settings, import,
authoring, unavailable-runtime screens, OS appearance matching, touch hardware,
screen-reader behavior and human visual acceptance remain outside this showcase.
See research/integration.md for exact production seams and required gates.

Remove this directory to undo the prototype. Additive vision capture has an
expected-base hash and recovery before-image recorded in capture-journal.json.
Do not restore a before-image over later edits. Compare the current fingerprint
first or remove only this task's appended entry. Existing dirty work is preserved.
No commit, push or installed application replacement was performed.


## Nonstandard question extension

Use Question formats in navigation for code prediction, a learner-filled trace,
a separate repair draft, code ordering, table completion, visual multiselect
and written reasoning. Responses survive in-tab format switches and navigation.
Reload clears them. Initial code prediction locks before the blank trace opens.
The code workspace preserves four source lines and indentation. A textarea
demonstrates editing without pretending to execute code or run tests.

References in navigation contains eight annotated sources plus 19 historical
project links. REFERENCES.md is its plain Markdown companion. Nothing is
fetched from these sites until the user opens a link.

Verified in-browser: all five format interactions, retained code/trace/table
drafts after switching, block-move status, and response previews. Verified
1440 px code composition and 390 px code, ordering, table, visual and reference
reflow. These checks do not establish real runtime scoring, exhaustive question
format parity, human accessibility acceptance or installed-app integration.
