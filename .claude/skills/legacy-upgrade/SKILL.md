---
name: legacy-upgrade
description: "Stub: upgrade legacy lessons and question artifacts for newer learning-UI capabilities (baseline audit, learning-value delta, identity and assessment preservation, bounded diff, validation, rollback). Not usable yet; its command surface has not shipped."
---

# Upgrade a legacy artifact (stub)

**Provenance:** stubbed 2026-08-14 (reframe slice 4b) per
`.planning/research/phase-16/14-synthesis.md` section 10.

**This skill is a stub; its command surface has not shipped.**

Intent: teach an agent client to enhance an older lesson or question
artifact for newer capabilities without losing anything: a baseline audit
first (current parse, identity, fingerprint, objectives, sources, rights,
media, assessment boundaries, plain rendering, rich rendering, validation),
a stated learning-value delta for every proposed change, preservation of
stable identity and source history, a bounded reviewable diff, deterministic
validation, and rollback.

It will cover: the audit-before-edit checklist, rejecting cosmetic novelty,
retaining an old artifact and linking a derived enhancement (with its
portability cost) when the old format cannot express it, keeping
assessment-semantic changes as separate reviewed revisions, and never
silently changing keyed content, assessment meaning, difficulty, or
objective alignment.

Ships after: subphase 16C (strategies, notes, and prototype convergence,
which owns legacy upgrade) and the Phase 17 UI work that gives upgrades a
target. Until then, follow the audit-before-editing rule in the "Course
artifact workflow" section of `.claude/CLAUDE.md` and the operation protocol
in `../OPERATION-CONTRACT.md`.
