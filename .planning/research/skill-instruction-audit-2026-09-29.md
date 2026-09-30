# Skill and instruction audit, September 29

Type: CURRENT-STATE. Audience: agent reference. Scope: all twelve Itembank skill entrypoints and both mirrors, their shared operation and assessment references, AGENTS.md, the Claude adapter, compact execution context and relevant workflow authority sections. This is a structural audit of the current source checkout, not a behavioral study or release acceptance.

## Applied findings

| Finding | Evidence | Repair |
|---|---|---|
| Old capabilities blocked existing workflows | Current CLI help exposes source, course graph, bindings, rights, proposals, staleness and package commands; skills still called these pending 14A/14B | Updated the shared operation table and build, absorption and curriculum routes. Command presence remains distinct from installed and human acceptance. |
| Three guided skills confused integration status with primitive availability | Agent UI uses the `Stub:` description prefix for unavailable state; manual primitives are present | Retained honest unavailable guided status and documented bounded manual discovery, lesson and media workflows. No UI integration was invented. |
| Tutoring assumed every answer advances and no explanation can ever be read | runtime.FEEDBACK_POLICIES holds wrong practice responses and defers formal feedback; session submit returns the runtime action | Follow returned transitions and released content. Do not infer correctness from silent formal output. Repaired invalid YAML in both tutoring mirrors. |
| OCR assumed every agent is text-only | Active harness may accept image input; OCR still lacks region evidence | Route by actual modality; keep OCR transcription and visual inspection distinct. Do not invent coordinates or source confidence. |
| Low confidence could be raised to satisfy lint | author-bank suggested raising confidence or accepting the warning | Investigate evidence or retain low confidence with a named review; lint cannot justify stronger epistemic confidence. |
| Compact executor blocked needed authority lookups | EXEC-CONTEXT forbade all contract reads; AGENT-WORKFLOW permits exact cited sections when a plan has a gap | Use compact context first, expand for the named uncertainty, and preserve authorized export and reviewed migration boundaries. |
| Onboarding carried old capability and permission claims | Claude adapter said no daemon and a frozen item list; root required unavailable provider memory and mixed commit permission with plan discipline | Use current help, permitted operational records and separate Git authorization. Local-only settings never waive a course policy. |
| Installed vision audit retained a placeholder invariant | Skill drift-audit item 8 still asked the installer to fill it | Named this project's runtime, privacy, rights, review, recovery and mirror invariants; kept routine task mechanics out of new vision entries. |

## Validation

Both skill trees remain byte-identical. Skill-creator quick_validate passes all 24 Itembank entrypoints. `scripts/preflight.py --quick` passed its ten fast gates, including guard, mirrors, schemas and path checks; Python/JavaScript full suites and clean-tree gate were deliberately skipped. Focused agent session, capability manifest, legacy-upgrade and agent-operation roundtrips passed. The three guided rows remain unavailable; reviewed proposal acceptance, stale refusal and synthetic undo still pass their existing tests.

Original pre-task instructions are preserved in archive/SKILL-INSTRUCTION-ORIGINALS-2026-09-29.md. All affected files were clean before this task. Existing product implementation edits, tests, README and backlog changes were left alone. No real course material was imported, no learner sitting was run, and no product runtime code, scorer, parser, schema or generated capability list was changed. These tests are source evidence; packaged, installed, human accessibility and learning-transfer acceptance remain unverified.

## Related project scope

Anarlog received bounded workflow and QA skill repairs, including Claude/Cursor trigger parity, package naming and staging-data preservation. Flight Lab and Snap received small AGENTS.md entry points to existing owners, with planning/physical and private/public boundaries respectively. The shared portable rules were reconciled and synced only to Itembank through an explicit repository target. This pass does not claim exhaustive auditing of every Anarlog release/database skill or all other repositories.

## Saved state

Project changes remain local for review and are not committed or pushed by this instruction pass. The planning vault records the cross-project result separately. No issue, comment, message, deployment, cloud setting or live QA reset was performed.
