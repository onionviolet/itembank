# Code question D1/D2 comparison

Ready for a formative human comparison. This remains a disposable prototype.
Weibao owns learner, visual, touch, screen-reader, and promotion acceptance.

From the repository root:

```sh
python3 -m http.server 8767 --bind 127.0.0.1 --directory prototypes/code-question-depth
```

Open http://127.0.0.1:8767/. Read the procedure before starting. Assign the next
order from 1 through 4 across fresh participants. Complete the two tasks, then
keep the downloaded JSON locally. The second download includes both trials.
The page has no autosave. Closing or reloading loses unsaved responses.
If downloads are blocked, expand Inspect or copy observations and copy the JSON
to a local file. The preview and download contain the same serialized record.

[Manual procedure and full text equivalent](manual.html) defines the task,
recording sheet, success criteria, first-mistaken-state capture, explanation
rubric, time boundaries, navigation counts, limitations, and human-only gates.
It works without scripts and contains no answer key. Review occurs after both
tasks, by a human, in a copy of the exported file or on paper.

The former browser-held expected trace and correctness check are removed.
Both depths commit a prediction before seeing the same diagnosis prompts.
Only D2 receives a blank learner-filled trace. Neither path executes code,
checks correctness, emits production evidence, or contacts external services.
The browser's only writes are downloads explicitly requested by the learner.
Counters are observations, not scores. No learning benefit has been established.

Verification:

```sh
node prototypes/code-question-depth/verify.mjs
```

The gate covers all four order assignments, trial transitions, required fields,
immutable initial prediction, timer arithmetic, human-review defaults, and key,
execution, and network absence in the active prototype. Browser observations
are recorded in the existing code-question audit. No full preflight was rerun.

Rollback: `before-comparison.zip` preserves the five original prototype files
and original audit. From the repository root, inspect then restore it with
`unzip -o prototypes/code-question-depth/before-comparison.zip` only if those
paths have no later work to preserve. Remove the added `manual.html` separately.
The archive restores the previous browser checker, so do not use the restored
version as this evidence packet. No production files or Git history changed.
