# Bilingual reader prototype

Disposable Phase 999.2 experiment, ready for a synthetic interaction trial. It is not a shipped reader, accepted format, scorer, evidence store, or learner-data migration.

## Try it

From the repository root:

```sh
python3 -m http.server 8768 --bind 127.0.0.1 --directory prototypes/bilingual-reader
```

Open http://127.0.0.1:8768. Tab to a highlighted word or click it. Change its status with the radio controls and check its repeated occurrences. The product question is whether lookup and shared word status help reading without interrupting it. Weibao owns that judgment and any promotion.

The static reading and complete three-entry glossary remain visible even when scripts fail or are disabled. They preserve reading meaning and glosses, but do not save status. Use localhost for interactive testing because module execution and storage on file URLs vary.

## Fixture and state contract

The text and glosses are agent-authored synthetic material with no external source or dictionary. `prototype.js` names the fixture, explicit lemma mappings, gloss locators, tokenizer version, and UTF-16 token offsets. Literal longest-match lookup preserves punctuation, whitespace, unmatched text and emoji exactly. It recognizes only three glossary entries and can match inside longer strings. It does not infer word boundaries, morphology, pronunciation in context, polysemy, or language-wide segmentation. The `zh` metadata direction inspired the display. Production `parse_terms` is neither imported nor changed.

All occurrences of a lemma in this one reading share one status. No status crosses reading identities. `new`, `learning`, and `known` are self-selected prototype labels, not learning evidence. The exact serialized passage, glossary and provenance identify the fixture. Changing them invalidates previous state rather than migrating it.

The single browser key is `itembank-prototype:bilingual-reader:v2:synthetic-reading-2`. Old v1 keys under `itembank-prototype:synthetic-reading-1:` are untouched. Browser origin, profile and port scope storage. No remote services, dependencies, telemetry, or production data are involved.

Cooperating tabs serialize writes through Web Locks when available. Every save also compares the raw saved base before replacing the single localStorage value. Storage events block further writes until **Reload saved state**. Save controls are disabled while a write is pending. Without Web Locks, compare then write is not atomic, so use one tab only. Non-cooperating scripts and storage clearing are outside this lock contract. This is not the production journal or recovery protocol.

## Portable prototype recovery

**Export prototype JSON** puts a complete exact-fixture state copy in the text box. Copy it to a local file. Paste that file's text into another browser running the same fixture, check the replacement box, then select **Restore prototype JSON**. Restore replaces all three word states and creates a fresh local revision. It carries no notes, scores, course data, historical revisions, browser settings, or accepted objects. Reset uses the same explicit replacement checkbox and writes all three states as New. Export before reset to make it reversible.

Restore rejects changed fixtures, unknown versions, unknown or missing states, invalid statuses, malformed JSON and extra top-level fields. Read failures, corruption and write failures preserve stored bytes and block further mutation. Reading stays available. Reload retries transient failures. Corrupt storage has no in-app repair path: preserve its raw value through browser storage tools, then remove only the exact v2 key and reload before restoring a valid export. This manual path and lack of a revision journal remain recovery blockers for production promotion.

## Verification recorded 2026-09-18

`node prototypes/bilingual-reader/verify.mjs` passes 12 grouped deterministic checks: lossless token ranges, repeated lemmas and provenance, longest literal overlaps, unmatched and mixed Unicode, one state slot per lemma, stale writes, independent-storage restore, reset isolation, invalid imports, corrupt/unavailable reads, failed writes, and exact static-text/gloss parity.

`python3 scripts/preflight.py --quick` passed every enabled gate. Python suites, JS suites and cleanliness gates were skipped by quick mode. Full repository suites were not run for this isolated prototype.

Chrome localhost observations through the browser UI:

- Tab focus opened 学习 lookup without a click. ArrowRight on New selected Learning and both 学习 buttons changed together. Enter lookup and ArrowLeft from Known updated all three 中文 buttons. A later focus check caught disabled controls dropping keyboard focus during saves. The fix restores focus when it falls to the body. The final browser check retained focus on the Learning radio and updated both 学习 occurrences.
- Export, confirmed reset, and confirmed restore changed both 学习 occurrences to New and back to Learning. A second tab's 中文 change blocked restore in the first tab with an explicit conflict message. Reload adopted all three Known occurrences.
- At 320 CSS pixels, viewport and body scroll width both measured 320 with mixed CJK/Latin, punctuation and emoji. Expanded provenance exposed the exact token range and glossary locator. Browser screenshots were inspected, but this does not establish human visual acceptance.
- With script execution disabled and the page reloaded, only the complete static reading and glossary appeared. Script execution and the temporary viewport override were restored afterward.

Independent empty-storage restore is a deterministic test, not a clean-machine offline restore claim. Human touch, screen-reader pronunciation and navigation, zoom, high contrast, real narrow-device interaction, learning effect, other browsers, RTL scripts and production crash recovery remain unverified. A generic Playwright connector failed to attach to its extension. The connected Chrome surface supplied the observations instead. No application state or permission settings were changed to repair that connector.

## Disposition and rollback

The owning disposition is IDEA-LEDGER `IL-20260918-02`. Phase 999.2 remains backlog with a prototype, not promoted. Before promotion, Weibao must settle the language/tokenizer/lemma policy, durable learner-owned object, rights acceptance for real sources, conflict and recovery design, and human acceptance gates. The source-to-course contract and sampled vision sections on direct reading, specific-content presentation, and deferred human review informed this bounded pass. No whole-vision audit or production implementation review was performed.

Changes are confined to the five files in this directory and the owning IDEA/Phase 999.2 planning records. Other dirty files were left alone. No commits or Git operations were performed beyond read-only inspection.

To discard the experiment, stop its localhost server, remove this directory, and remove only the exact prototype keys named above from that origin after preserving any wanted export. Keep the dated planning evidence and mark the experiment withdrawn if its disposition changes. Reset alone leaves the code and all unrelated browser storage intact.

Exact next action: Weibao reads the synthetic passage once, marks 学习 as Learning, and decides whether repeated-word tracking helps the reading flow enough to justify a real-source prototype.

## 2026-09-18: word-anchored lookup refinement

The definition now floats beside the exact hovered, focused or clicked word
occurrence. Word status and provenance sit behind a disclosure so the default
popup stays short. Arrow Down enters the popup. Escape closes it and returns
focus when focus was inside. Pointer travel into the popup keeps it open.
Outside clicks dismiss it. Resize and scroll reposition it within the viewport.

Browser observations confirmed hover on the second 学习 occurrence, keyboard
entry and Escape focus return, and a 320px screenshot with the popup inside the
viewport. Changing 中文 to Learning updated all three occurrences. The test
returned them to New. Twelve deterministic checks and quick preflight passed.
Touch-device behavior and screen-reader acceptance remain unverified.

The vision audit retains its existing legacy traceability backlog. This
refinement changes only prototype presentation and records the feedback in
the existing vision and idea owners. No code execution or production behavior
was added. The Code Learner source comparison lives in the existing
code-question depth audit rather than a second coding roadmap.

## 2026-09-18: smaller speech-bubble refinement

P-20260918-01 supersedes the prior hover composition. Hover and focus show only
pronunciation and meaning in a bubble capped at 220px. Prefer above the word
and fall below near the viewport top. Click, tap or Arrow Down reveals controls
in normal document flow. Escape returns focus from controls. Outside focus
dismisses lookup. Word-state persistence is unchanged.

Browser inspection measured 36px bubble height for two fixture glosses,
verified the second occurrence anchor, keyboard controls and Escape return,
and confirmed no document overflow at 320px. Twelve deterministic checks and
quick preflight passed. Dense multiline text and physical touch still need
human review. This is a prototype repair, not whole-app acceptance.
