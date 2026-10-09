# Native reading workspace comparison

This preview serves the current production reading renderer on a disposable
synthetic course. It uses an original, deliberately long trail-counter sample
to compare the same material in Read, Study and Notebook modes.

```sh
python3 prototypes/reading-modes-20261001/preview.py
python3 prototypes/reading-modes-20261001/preview.py --verify
```

The first command prints a local URL. Press Enter to stop the daemon and remove
its course, source and private-note files. It never opens learner roots.
The second command uses already installed Chrome through Python Playwright,
checks actual native pages, and stops its daemon automatically. Screenshots
and measurements go to `.reasonix/reading-modes-20261001/` by default.

These are source-preview and automated interaction observations. They do not
establish installed-app, physical touch, screen-reader or human preference
acceptance. Implementation scope, ranked review and recovery belong to
`.planning/research/overall-improvements-2026-10-01.md`.
