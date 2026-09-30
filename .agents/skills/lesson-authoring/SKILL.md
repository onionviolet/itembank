---
name: lesson-authoring
description: "Stub: the integrated guided lesson-authoring workflow has not shipped. Existing lesson grammar, rendering and reviewed course proposals support the bounded manual workflow below."
---

# Author a source-grounded lesson

The guided skill remains unavailable. Semantic lesson capabilities and reviewed proposals exist; their presence does not mean this skill is wired into every agent UI.

Read [OPERATION-CONTRACT.md](../OPERATION-CONTRACT.md), the current source and course policy, then `python itembank.py spec`. Choose a lesson only when direct reading or an adequate existing artifact does not meet the objective. Cite exact source locators, preserve source wording when quoting and label supplementary synthesis.

Author through the current `## LESSON` or `[LESSON-SRC:]` contract. Read the relevant grammar before adding semantic roles, staged reveals, checks or media. Do not invent fields. Keep core meaning coherent in plain Markdown and supply useful static and accessible alternatives for rich behavior. Teaching checks are distinct from keyed assessment content and independent mastery evidence.

For a configured course proposal, inspect `python itembank.py course agent-operation --help`. Its start, preview, revise, accept, reject and undo actions retain reviewed state; only configured supported skill IDs may start an operation. Do not pass this unavailable skill ID as if registration were implementation. Preserve draft fingerprints and reviewer authority.

Lint the bank, inspect the plain lesson and render its learner-facing form with `lesson`, `study` or the relevant daemon view. Deterministic checks do not certify human accessibility or learning quality. Present a bounded diff, accept only within granted authority, and verify the accepted artifact and tested recovery path.
