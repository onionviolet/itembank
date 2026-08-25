#!/usr/bin/env python3
"""itembank: author, validate and render exam-style question banks in markdown.

Built because a prose format spec does not fail loudly. An AI handed a prompt
template can conform to it or not with no way to tell which, so banks go
silently malformed and nobody notices until a renderer reports the wrong item
count. The fix is a machine-checkable contract: `itembank spec` tells an
authoring agent the format, `itembank lint` tells it exactly what it got wrong.

  itembank spec                 print the format contract (the AI-facing entry point)
  itembank schema [NAME]        print a published JSON contract; --all emits everything
                                 (the format contract, all five documents, the command
                                 sequence to run a session) in one self-contained object
  itembank lint  BANK.md        validate; errors exit non-zero, warnings advise
  itembank build BANK.md [OUT]  offline HTML quiz; holds the key, saves nothing
  itembank serve BANK.md        the graded sitting: the process scores and records
  itembank stats BANK.md        item mix, objective coverage, answer-position skew
  itembank start BANK.md        start a resumable, agent-readable assessment
  itembank next SESSION.json    return the next item without its answer key
  itembank submit SESSION.json  score the current response and advance the session
  itembank report SESSION.json  summarize the recorded evidence
  itembank study BANK.md [OUT]  render a flashcard and Learn surface
  itembank export BANK.md OUT   export Basic or Cloze Anki TSV
  itembank day   PLAN.md        today's work across every subject, ticked and logged
  itembank guard [DIR]          fail if a real question bank was committed

Scoring is dichotomous on every item type, matching the NREMT rule that no
credit is given for a partially correct response. A half mark hides the gap the
item exists to find.

This file is the entry point and the public surface, nothing more. The tool is
four layers, and the boundaries between them are the design:

  model.py     what a bank is and what makes one invalid
  runtime.py   scoring, sessions, and what a surface may see. The only scorer.
  server.py    one loopback HTTP server, for the surfaces that need a browser
  surfaces/    quiz, study, day, export, sessions, CLI. All of them clients.

Python standard library only. No network, no services, no dependencies, and no
install step: `python itembank.py` from a checkout is the whole thing.
"""
# D-07: releases are tagged plain vX.Y.Z with no pre-release or build suffix,
# because the updater compares version components as integers.
__version__ = "0.3.0"

import os
import sys

# Run correctly from any working directory, and from a symlink or a `day` wiring
# entry that names an absolute path. Without this, `python /elsewhere/itembank.py`
# imports nothing.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import (BANK_FILE_HINTS, KEYS_UNCHECKED, LESSON_UNCHECKED,        # noqa: E402
                   LETTERS, LINT_CODES, LintError, SPEC, TERMS_UNCHECKED,
                   CHECK_UNRESOLVED_COPY, GATE_VALUES,
                   assign_ids, collapse, content_fingerprint, grab, lint, load,
                   lesson_slug, new_item_id, notes, parse_bank, parse_lesson,
                   parse_key_blocks, parse_question, parse_terms, section)
from runtime import (FEEDBACK_POLICIES, FIELD_SEP, HINT_TIERS, ITEM_VERSION,  # noqa: E402
                     PAIR_SEP, REPORT_VERSION, SESSION_UPGRADES,
                     SESSION_VERSION, answer_text, authored_hint,
                     canonical_key, canonical_response, explain_payload,
                     glossable, new_teaching_record, normalize_answer,
                     page_item, public_item, read_session, reconcile_teaching_state,
                     response_text, score_response, selection_feedback,
                     session_path,
                     session_summary, session_view, teaching_key,
                     teaching_payload, teaching_transition, upgrade_session,
                     write_session)
from selection import (DEFAULT_COUNT, SPEC_FIELDS, SELECTION_MODES,           # noqa: E402
                       expand_spec, select)
from surfaces.cli import main                                                  # noqa: E402
from surfaces.day import (ANKI_ADDON_ID, DAY_LANES, FLOOR_LANES, anki_read,   # noqa: E402
                          day_history, day_info, day_page, day_status,
                          day_streak, day_text, lane_behind, lane_files,
                          lane_load, lint_lane_decks, lint_lane_paths,
                          load_day_log, parse_lanes, parse_plan, resolve_notes,
                          wiring_bases, write_day_log)
from surfaces.migrate import (read_attempt_md, read_legacy_session, scan_legacy,  # noqa: E402
                              source_key)
from evidence import (EVENT_SCHEMA_VERSION, INDEX_VERSION, KNOWN_EVENT_TYPES,  # noqa: E402
                      SELECTION_EVENT_TYPE,
                      GATE_MODES, GATE_SKIP_EVENT_TYPE, LESSON_GATE_CONTEXT,
                      append_event, append_line, attempt_number,
                      day_log_from_events, day_tick_event, dedupe_key,
                      ensure_index,
                      event_by_id, event_matches, evidence_dir, events,
                      gate_outcome_split, gate_skip_event, gate_state,
                      idempotency_canon, index_for_log, index_path,
                      index_stale, iter_raw, live_events, locked, log_path,
                      mark_event, marks_by_event, new_event_id,
                      objective_history, objective_rollup, recent_dedupe_keys,
                      hint_event, hint_events, teaching_outcomes,
                      rebuild_index, render_attempt_md, render_daily_log,
                      render_session_json,
                      response_event, retracted_ids, retraction_event,
                      selection_event,
                      key_review_event, session_events, subject_of,
                      term_lookup_event, utc_now)
from schema_validate import SUPPORTED, SchemaError, validate                  # noqa: E402

__all__ = [
    "ANKI_ADDON_ID", "BANK_FILE_HINTS", "DAY_LANES", "EVENT_SCHEMA_VERSION",
    "FEEDBACK_POLICIES",
    "DEFAULT_COUNT", "FIELD_SEP", "FLOOR_LANES", "INDEX_VERSION", "ITEM_VERSION",
    "HINT_TIERS",
    "KNOWN_EVENT_TYPES",
    "GATE_MODES", "GATE_SKIP_EVENT_TYPE", "GATE_VALUES",
    "LESSON_GATE_CONTEXT",
    "KEYS_UNCHECKED", "LESSON_UNCHECKED", "LETTERS", "LINT_CODES", "LintError",
    "TERMS_UNCHECKED",
    "PAIR_SEP", "REPORT_VERSION", "SELECTION_EVENT_TYPE", "SELECTION_MODES",
    "expand_spec",
    "SESSION_UPGRADES", "SESSION_VERSION", "SPEC", "SPEC_FIELDS",
    "SUPPORTED", "SchemaError",
    "__version__",
    "anki_read", "answer_text", "append_event", "append_line", "assign_ids",
    "attempt_number", "canonical_key", "canonical_response", "collapse",
    "content_fingerprint", "day_history", "day_info",
    "day_log_from_events",
    "day_page", "day_status", "day_streak", "day_text", "day_tick_event", "dedupe_key",
    "ensure_index", "event_by_id", "event_matches", "evidence_dir", "events",
    "explain_payload",
    "glossable", "grab", "gate_outcome_split", "gate_skip_event", "gate_state", "hint_event", "hint_events", "idempotency_canon",
    "index_for_log", "index_path",
    "index_stale", "iter_raw",
    "lane_behind",
    "lane_files", "lane_load", "lesson_slug", "lint", "lint_lane_decks", "lint_lane_paths",
    "live_events", "load", "load_day_log", "locked", "log_path",
    "main", "mark_event", "marks_by_event", "new_event_id", "new_item_id",
    "new_teaching_record", "normalize_answer", "notes",
    "objective_history", "objective_rollup", "page_item", "parse_bank",
    "parse_lanes",
    "parse_key_blocks", "parse_lesson", "parse_plan", "parse_question",
    "parse_terms",
    "public_item", "read_attempt_md", "read_legacy_session", "read_session",
    "rebuild_index", "recent_dedupe_keys",
    "render_attempt_md", "render_daily_log", "render_session_json", "resolve_notes",
    "response_event", "response_text", "retracted_ids", "retraction_event",
    "scan_legacy",
    "expand_spec", "reconcile_teaching_state", "score_response", "section", "select",
    "selection_feedback",
    "selection_event",
    "session_events", "session_path",
    "key_review_event", "session_summary", "session_view", "source_key",
    "subject_of", "teaching_key", "teaching_outcomes", "teaching_payload",
    "teaching_transition",
    "term_lookup_event", "upgrade_session", "utc_now",
    "CHECK_UNRESOLVED_COPY",
    "authored_hint",
    "validate", "wiring_bases", "write_day_log", "write_session",
]

if __name__ == "__main__":
    main()
