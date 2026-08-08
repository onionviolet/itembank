---
phase: 3
slug: lesson-format-in-app-reader
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-08
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None — direct script execution. No pytest, no unittest runner, no framework dependency (stdlib-only project constraint). |
| **Config file** | none — no `pyproject.toml`, no `setup.py`, no `requirements.txt` exists or may be added |
| **Quick run command** | `python tests/lesson_roundtrip.py` |
| **Full suite command** | `for f in tests/*_roundtrip.py; do python "$f" || exit 1; done` (CI iterates `tests/*.py` directly) |
| **Estimated runtime** | ~5 seconds quick, ~60 seconds full |

Test convention: a `tests/<name>_roundtrip.py` file, executable directly, printing `FAIL: <msg>`
and exiting 1 on failure. Helper `fail(msg)` per `.planning/codebase/TESTING.md`.

---

## Sampling Rate

- **After every task commit:** Run `python tests/lesson_roundtrip.py`
- **After every plan wave:** Run the full suite
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

*Filled by the planner 2026-08-08. One row per task, mapped to a LESSON-xx requirement.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| T1 | 03-01 | 1 | LESSON-02 | — | checkpoint:decision — D-04's one-way door on the content fingerprint; no code, no command | checkpoint | *(none — blocking human decision)* | n/a | ⬜ pending |
| T2 | 03-01 | 1 | LESSON-01, LESSON-02, LESSON-03, LESSON-06 | T-3-01, T-3-03, T-3-05 | every text run escaped; `<stem>` resolved through the startup allowlist; reader reaches no scorer and builds no key | integration + unit (tracer) | `python tests/lesson_roundtrip.py` | ❌ created by this task (Wave 0) | ⬜ pending |
| T3 | 03-01 | 1 | LESSON-06 | T-3-06 | the URL fragment is compared against ids already in the page's own array, never interpolated into markup | integration | `python tests/lesson_roundtrip.py` | ✅ after T2 | ⬜ pending |
| T1 | 03-02 | 2 | LESSON-01 | T-3-02 | out-of-tree and absolute `[LESSON-SRC:]` paths refused before any open, using the separator-suffixed containment shape | unit | `python tests/lesson_roundtrip.py` | ✅ | ⬜ pending |
| T2 | 03-02 | 2 | LESSON-06 | T-3-04 | an unreadable source degrades to a 200 page on both surfaces, never an exception | integration | `python tests/lesson_roundtrip.py` | ✅ | ⬜ pending |
| T1 | 03-03 | 3 | LESSON-04 | T-3-04 | every lesson check returns a finding rather than raising; `lint(qs)` unchanged for existing callers | unit | `python tests/lesson_roundtrip.py` | ✅ | ⬜ pending |
| T2 | 03-03 | 3 | LESSON-04 | T-3-09 | lint echoes the authored path, never a resolved absolute one | contract (CLI + schema) | `python tests/lesson_roundtrip.py` | ✅ | ⬜ pending |
| T3 | 03-03 | 3 | LESSON-04 | T-3-08 | published codes, schema enum and accepted namespace prefixes asserted equal in both directions | contract | `python tests/lesson_roundtrip.py` | ✅ | ⬜ pending |
| T1 | 03-04 | 4 | LESSON-06 | T-3-10, T-3-04 | fenced content escaped and verbatim, info string sanitised into the class attribute, malformed fence does not raise | unit | `python tests/lesson_roundtrip.py` | ✅ | ⬜ pending |
| T2 | 03-04 | 4 | LESSON-06 | T-3-01, T-3-11 | text runs escaped after structure resolution; only relative or http/https targets become links | unit + integration | `python tests/lesson_roundtrip.py` | ✅ | ⬜ pending |
| T1 | 03-05 | 5 | LESSON-06 | T-3-12 | `--ref` resolved by slug equality — never interpolated, never used as a path or a pattern | unit + CLI | `python tests/lesson_roundtrip.py` | ✅ | ⬜ pending |
| T2 | 03-05 | 5 | LESSON-06 | T-3-04, T-3-13 | every no-lesson and unreadable-source path writes a page and exits 0; one status line, nothing on stdout | CLI | `python tests/lesson_roundtrip.py` | ✅ | ⬜ pending |
| T1 | 03-06 | 6 | LESSON-05 | T-3-14, T-3-15, T-3-08 | `SPEC` extended additively with every existing substring intact; the containment rule documented, not only enforced | smoke | `python tests/lesson_roundtrip.py` | ✅ | ⬜ pending |
| T2 | 03-06 | 6 | LESSON-05 | — | checkpoint:human-verify — spec-sufficiency trial plus the two UI-SPEC backstop rows | manual | *(none — see Manual-Only Verifications)* | n/a | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**Sampling continuity:** twelve of the fourteen tasks carry `<automated>`; the two that do not are
checkpoints (03-01 T1 and 03-06 T2), and neither is adjacent to another checkpoint, so no three
consecutive tasks run without an automated verify.

**Every plan additionally runs the full suite** (`for t in tests/*.py; do python "$t" || exit 1; done`)
as a second `<automated>` on every task, mirroring CI's own discovery loop, because six of this phase's
files are shared with existing surfaces.

---

## Wave 0 Requirements

Both gaps are closed by **plan 03-01, Task 2**, whose first move is to write the fixture and the
failing test before any implementation — the tracer starts red, so its own `<automated>` names a file
that exists by the time it runs.

- [ ] `tests/lesson_roundtrip.py` — new file, created by 03-01 T2 with the tracer's end-to-end
      assertions; plans 03-02 through 03-06 extend this one file rather than adding parallel ones
- [ ] `fixtures/lesson_bank.md` — new synthetic fixture, created by 03-01 T2 with a `## LESSON`
      section, two `###` headings (one referenced, one orphan) and `[LESSON-REF:]` tagged items.
      Plan 03-04 T1 adds the list, table and fenced-code-with-info-string material (the Phase 9 seam)
      once the renderer supports it
- [ ] `fixtures/sample_bank.md` — **unchanged**, and used as the LESSON-03 regression: 03-01 T2
      asserts its parse result (6 items, the mc/multi/table/build/dnd/short type sequence, and the
      first item's stem, options and correct answers) against literals recorded in the test

Fixtures added later in the phase, listed here so the inventory is whole: `fixtures/lesson_shared.md`
and `fixtures/lesson_src_bank.md` (03-02, the shared-source pair), `fixtures/lesson_broken_src_bank.md`
(03-03, the fourth lint code), and lesson material added to the existing `fixtures/broken_bank.md`
(03-03, so CI's existing schema-validation step exercises the three inline lesson codes).

No framework install — the project forbids one.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| A full-chapter lesson (~20,000 words) renders and scrolls without a perceptible stall | LESSON-06 | Perceived-performance judgment; no timing threshold is meaningful without a human reading it | Open `/lesson/<bank>` on the largest available fixture, scroll top to bottom, confirm no visible stall |
| `itembank lesson` on a very large `[LESSON-SRC:]` file does not read as a hang | LESSON-06 | Whether silence reads as a hang is a human judgment, not a measurement | Run the CLI against the largest fixture and observe |
| `spec` output is sufficient for an authoring agent with no source access | LESSON-05 | The success criterion is about a model's first-try success, testable only by trying it | Give a model only `itembank spec` output and ask it to author a valid lesson; it must lint clean on the first attempt |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
