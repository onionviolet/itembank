---
name: discovery-and-binding
description: "Stub: discover sources and artifacts across approved roots and bind them to courses and objectives (root scopes, identity reconciliation, link and import semantics, conflicts, no mutation during inventory). Not usable yet; its command surface has not shipped."
---

# Discover and bind sources and artifacts (stub)

**Provenance:** stubbed 2026-08-14 (reframe slice 4b) per
`.planning/research/phase-16/14-synthesis.md` section 10.

**This skill is a stub; its command surface has not shipped.**

Intent: teach an agent client to run Loop A of the synthesis (declare read
roots and rights, scan read-only, identify by stable ID plus fingerprint,
preview and classify, surface duplicates, moves, conflicts, and unsupported
files, choose link, import, copy, move, or ignore, bind to objectives,
validate, checkpoint, and index) without mutating anything during
inventory and without ever merging artifacts by name similarity.

It will cover: root scope declaration, identity versus fingerprint versus
path reasoning (same ID with divergent bytes is a conflict; same
fingerprint with different IDs suggests a copy; a moved path with the same
ID is a move candidate), the distinct link, import, copy, move, and
supersede operations, conflict surfacing, and the derived disposable index.

Ships after: subphases 14A (identity, lifecycle, and operation prototype)
and 14B (graph and course package prototype), which supply the stable IDs,
fingerprints, operation journal, and binding records this skill would
document. Until then, discovery is the manual read-only inventory described
in `build-course` step 3 and `../OPERATION-CONTRACT.md`.
