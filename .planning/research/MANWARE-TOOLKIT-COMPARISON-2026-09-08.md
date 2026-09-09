# Manware toolkit comparison

Date: 2026-09-08. Status: bounded research, recommendations only.

## Finding

The toolkit is a useful lightweight coding-tutor prompt pack, not a replacement
for Itembank. Its inspected default branch contains prompts, skills, and manual
learning logs. Itembank provides a deterministic assessment runtime and a broader
source-to-course contract. Product direction is not proof that every planned
course or CS Dojo interaction has shipped.

Sources inspected: upstream README, complete default-branch file inventory,
global instructions, hint, autopsy, retrieve, and API prompts, and examination
skill. Other agent branches were not reviewed. Upstream reference:
https://github.com/i-am-manware/Manware-s-AI-Learning-Toolkit/tree/copilot

Local comparison sampled SOURCE-TO-COURSE.md, AGENT-WORKFLOW.md, STATE.md,
USER-VISION.md's CS Dojo interpretation, guiding-questions, and the personal
coached-build skill. No runtime module was read in full. This is a workflow
comparison, not a runtime correctness or learning-efficacy audit.

## Reconciled recommendations

| ID | Idea | Existing overlap and disposition | Owner and next gate |
| --- | --- | --- | --- |
| F1 | Commit to an output prediction before running code | Already explicit in the course learning loop and CS Dojo direction. Prototype concrete input-tracing exercises rather than adding another teaching framework. | CS Dojo planning owner. Revisit with the first executable coding activity. |
| F2 | Reflect on a meaningful bug through the original belief, actual behavior, and missed evidence | Useful specific exercise beyond the sampled coached-build instructions. Prototype as a learner-owned reflection linked to its activity. | CS Dojo planning owner. Try one reflection and a later independent variant. Avoid treating a reflection as a settled score. |
| F3 | Short retrieval warm-up mixing prediction, debugging, comparison, and transfer | Useful interaction packaging. Reuse existing evidence and activity selection rather than importing four parallel learning logs. | Practice strategy owner. Revisit when course-linked coding evidence exists. |
| F4 | API exploration through purpose, assumptions, alternatives, tradeoffs, and failure modes | Useful reusable exercise with primary documentation and a verification experiment. Prototype within a source-grounded lesson. | Course-authoring owner. Revisit with an actual API learning objective. |

The toolkit has a low setup burden and concrete commands. Itembank has stronger
assessment boundaries. The inspected personal coached-build skill already adds
worked examples, faded support, deadline handling, and a later unaided variant.
These differences make wholesale replacement inappropriate.

Do not directly import the toolkit's agent-selected hint levels or treat its
confidence assessment as a settled mark. Itembank's guiding-questions contract
states: "The runtime owns the hint ladder" and "you never decide the tier."
Retain the teaching intent through runtime-permitted disclosure and descriptive
or pending evidence. Reconsider mappings if an explicitly separate ungraded
coding activity defines its own permitted assistance contract.

No LICENSE file appeared in the inspected default-branch inventory. Adapt ideas
in original wording. Verify permission before copying upstream prompt text.
No upstream text or code was installed, and these proposals do not change scope.

## Publication result

The user explicitly requested public visibility. GitHub reported PRIVATE before
the change and PUBLIC afterward for https://github.com/onionviolet/itembank.
Only visibility changed. No local commits or uncommitted edits were pushed.

A fresh remote clone at 9edd9e825afb251447fd1d1075ee300f572b3f3d passed
`python3 itembank.py guard .` with zero offending files. Common credential
patterns produced no matches in its checkout or fetched history. Sensitive-name
history inspection surfaced synthetic session fixtures and schemas. These are
bounded checks, not a comprehensive historical privacy or secret audit.

This report is the only local file created by this review. It can be removed to
undo the research artifact. Making the repository private again cannot retract
copies already obtained by others.

Local quick preflight passed its other executed gates but failed skill mirrors:
`author-bank/_attempts` exists only in `.agents/skills`. This review did not
change either skill tree. Full Python and JavaScript suites were not run.
