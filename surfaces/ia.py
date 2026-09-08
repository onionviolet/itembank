#!/usr/bin/env python3
"""The information-architecture read models for Phase 16B.

This module holds the closed vocabularies, the copy tables, and the pure read
models behind the Activity view, the offline help panel, the course shelf, the
course areas, the mode-layer table, and the degraded-state banners. It reads
durable records and never writes one. It never imports `runtime`, so it cannot
score; it never opens a journal file for appending or replacing; and the only
files it ever creates are the two small per-install state files under `_ia/`,
which are app state rather than evidence and rather than settings. It imports
`model` for exactly one name, `lesson_slug`, because the anchor scheme must be
the shipped one and a second slug implementation would be a second anchor
vocabulary. `lesson_slug` is the only name this module takes from `model`. `sample_course`
is the second and last module imported from outside `surfaces/`.

The Activity area named in this module means durable agent and maintenance
jobs: a long-running discovery, an import that is waiting on a decision, a
reconciliation that was interrupted. It is a different object from
`REQUIREMENTS.md`'s `ACTIVITY-01`, `ACTIVITY-02`, and `ACTIVITY-03` family of
purpose-first learner questions. They share a word and not a schema, and
nothing in this module renders a learner question (Decision D6).

`ITEMBANK_IA_NO_JOURNAL=1` is a test-only degradation switch. Phase 16B's own
precondition check guarantees `journal.py` is present in this tree, so the
not-yet-available Activity state would otherwise be unreachable and the phase
would ship a state it never executed. Setting the variable makes
`activity_view_state` take the same branch a build without `journal.py` takes.
It is read only when the `journal` argument is omitted.
"""
import json
import os

import model
import sample_course


# The twelve offline help codes this phase can route to. Sorted so the tuple
# is a stable published vocabulary rather than an authoring order.
IA_HELP_CODES = tuple(sorted({
    "ia.activity_unavailable",
    "ia.agent_unavailable",
    "ia.cancelled",
    "ia.course_corrupted",
    "ia.crash_recovered",
    "ia.disk_full",
    "ia.future_schema",
    "ia.offline",
    "ia.permission_denied",
    "ia.route_not_found",
    "ia.sample_course_removed",
    "ia.walkthrough_unavailable",
}))

# Every state one durable job can display in the Activity view.
ACTIVITY_JOB_STATES = ("needs_input", "in_progress_no_estimate",
                       "in_progress_known", "completed", "failed",
                       "cancelled", "interrupted", "unavailable")

# Tuple order is the deterministic degraded-banner precedence locked by
# D-16B-9: the first member present wins the banner slot, and every other
# fired state stays reachable through its own help page.
DEGRADED_STATES = ("crash", "cancelled", "disk_full", "offline",
                   "permission_denied", "future_schema", "agent_unavailable",
                   "course_corrupted")

# What a course tile or an area can be asking of the learner right now.
ATTENTION_STATES = ("up_to_date", "due", "pending_review", "needs_input",
                    "needs_reconciliation", "last_valid_overview")

# Ordered lowest authority first, so a later member overrides an earlier one.
MODE_LAYERS = ("learner_preference", "author_strategy", "objective_constraint",
               "accommodation_override", "instructor_policy",
               "runtime_authority", "system_safety")

# The two layers no learner preference and no instructor policy can move.
MODE_LAYERS_FIXED = ("runtime_authority", "system_safety")

# Notes is deliberately absent: D4 gives Notes no dedicated route and renders
# it only as a contextual panel inside Learn and Evidence.
COURSE_AREAS = ("overview", "learn", "practice", "test", "map", "sources",
                "build", "agent", "evidence")

# The locked Activity copy, verbatim from the 16B-UI-SPEC Activity Contract.
ACTIVITY_COPY = {
    "needs_input": "Needs your input",
    "in_progress_no_estimate": "In progress: no estimate.",
    "in_progress_known": "Step {n} of {N}: {stage}",
    "completed": "Completed",
    "failed": "Failed: {reason}",
    "cancelled": ("Cancelled. Partial results are marked below and were not "
                  "saved as final."),
    "interrupted": "Interrupted: resume available.",
    "unavailable": ("Activity isn't available yet in this build. Check back "
                    "after your next update."),
}

# Existing semantic token names assigned by 16B-UI-SPEC, as bare names with no
# leading dashes and no color value. Phase 16B introduces no new token, no new
# color, no new spacing value, and no new typography size; every name here is
# one Phase 17A already owns.
ACTIVITY_TOKENS = {
    "needs_input": "pending",
    "in_progress_no_estimate": "pending",
    "in_progress_known": "pending",
    "completed": "ok",
    "failed": "bad",
    "cancelled": "warn",
    "interrupted": "warn",
    "unavailable": "unknown",
}

# The eight keys one Activity job dict carries, and no others. This allowlist
# is the metadata boundary: a journal entry's before-image, its raw content
# fields, and any byte payload are never copied out of the journal into a
# rendered page.
JOB_KEYS = ("entry_id", "object_kind", "state", "label", "token", "intent",
            "timestamp", "help_code")

_UNSET = object()

_NO_JOURNAL_ENV = "ITEMBANK_IA_NO_JOURNAL"


def _basename_only(value):
    """D9: path-bearing copy shows the bank-author-written basename only,
    never a resolved absolute path. Reuses the shipped `lesson.src_unreadable`
    precedent rather than inventing a second disclosure rule."""
    text = "" if value is None else str(value)
    if os.sep in text or "/" in text or "\\" in text:
        return os.path.basename(text.replace("\\", "/").rstrip("/"))
    return text


def _reason_of(entry):
    """The journal's own recorded refusal text.

    The landed `journal.py` records a refusal as `code` plus `message`; the
    16B plan text called that field `reason`. Both names are read so a
    landed entry and a plan-text-shaped entry map to the same display, and
    neither is a second entry schema.
    """
    for name in ("message", "reason"):
        text = entry.get(name)
        if text:
            return str(text)
    return "no reason recorded"


def _intent_of(entry):
    """One line of the job's own recorded intent.

    The landed `journal.py` has no single `intent` field; its equivalent is
    the recorded `operation` over the recorded `path`. The path half runs
    through the basename rule, so no resolved absolute path reaches a page.
    """
    text = entry.get("intent")
    if text:
        return _basename_only(text)
    operation = entry.get("operation") or ""
    origin = entry.get("origin")
    if not operation and isinstance(origin, dict):
        operation = origin.get("operation") or ""
    target = _basename_only(entry.get("path"))
    if operation and target:
        return "%s %s" % (operation, target)
    return operation or target


def _positive_int(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _label_for(state, entry):
    """`ACTIVITY_COPY[state]` with the entry's own recorded fields
    substituted. No percent form exists in the table, so no percent can be
    produced here (D7)."""
    text = ACTIVITY_COPY[state]
    if state == "in_progress_known":
        return (text.replace("{n}", str(entry.get("step")))
                    .replace("{N}", str(entry.get("steps_total")))
                    .replace("{stage}", str(entry.get("stage") or "")))
    if state == "failed":
        return text.replace("{reason}", _reason_of(entry))
    return text


def _job(entry, state):
    return {
        "entry_id": entry.get("entry_id"),
        "object_kind": entry.get("kind"),
        "state": state,
        "label": _label_for(state, entry),
        "token": ACTIVITY_TOKENS[state],
        "intent": _intent_of(entry),
        "timestamp": entry.get("timestamp"),
        "help_code": "ia.agent_unavailable" if state == "failed" else None,
    }


def _unreadable_job():
    return {
        "entry_id": None,
        "object_kind": None,
        "state": "failed",
        "label": ACTIVITY_COPY["failed"].replace("{reason}",
                                                 "unreadable journal entry"),
        "token": ACTIVITY_TOKENS["failed"],
        "intent": "",
        "timestamp": None,
        "help_code": "ia.agent_unavailable",
    }


def _pending_state(entry):
    """The display state for a prepared entry nothing has resolved yet."""
    if entry.get("step") is None:
        return "needs_input"
    if _positive_int(entry.get("steps_total")):
        return "in_progress_known"
    return "in_progress_no_estimate"


def activity_view_state(root, journal=_UNSET):
    """The Activity view's whole state as a plain dict. Performs no write.

    Passing `journal=None` forces the not-yet-available branch, which is how
    a build without `journal.py` behaves and how that state is exercised in a
    tree where `journal.py` is present. Omitting the argument imports
    `journal` and falls back to the same branch on `ImportError`, or when
    `ITEMBANK_IA_NO_JOURNAL` is set to `1`.

    Every key of every returned job is metadata drawn from `JOB_KEYS`. A
    journal entry's before-image, its raw content fields, and any byte
    payload are never copied into the result, because the UI-SPEC's Journal
    metadata boundary clause keeps them out of a rendered page.
    """
    if journal is _UNSET:
        if os.environ.get(_NO_JOURNAL_ENV) == "1":
            _j = None
        else:
            try:
                import journal as _j
            except ImportError:
                _j = None
    else:
        _j = journal

    if _j is None:
        return {"available": False, "code": "ia.activity_unavailable",
                "notice": ACTIVITY_COPY["unavailable"],
                "needs_input": [], "jobs": []}

    raw = list(_j.entries(root))

    resolved = {}
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        if entry.get("state") not in ("applied", "refused"):
            continue
        target = entry.get("resolves_entry")
        if target:
            resolved[target] = entry

    jobs = []
    for entry in raw:
        if not isinstance(entry, dict) or not entry.get("entry_id") \
                or not entry.get("state"):
            jobs.append(_unreadable_job())
            continue
        if entry.get("state") != "prepared":
            continue
        resolver = resolved.get(entry.get("entry_id"))
        if resolver is None:
            object_state = _j.object_state(root, entry.get("object_id"))
            if object_state == "interrupted":
                state = "interrupted"
            elif object_state == "conflict":
                state = "needs_input"
            else:
                state = _pending_state(entry)
            jobs.append(_job(entry, state))
            continue
        if resolver.get("cancelled") is True:
            state = "cancelled"
        elif resolver.get("state") == "applied":
            state = "completed"
        else:
            state = "failed"
        merged = dict(entry)
        for name in ("message", "reason", "code"):
            if resolver.get(name):
                merged[name] = resolver[name]
        jobs.append(_job(merged, state))

    jobs.sort(key=lambda job: (job["entry_id"] or ""))
    jobs.sort(key=lambda job: (job["timestamp"] or ""), reverse=True)

    return {
        "available": True,
        "code": None,
        "notice": "",
        "needs_input": [job for job in jobs if job["state"] == "needs_input"],
        "jobs": jobs,
    }


# The exact sentence an unrecognized code answers with. A code nobody wrote an
# entry for is still answered, never refused.
HELP_FALLBACK_COPY = "No additional help is available for this yet."

# The whole offline help corpus, as literal strings inside this module. No file
# is opened and no socket is used to render a help page, because a help path
# that reaches for the network becomes unavailable exactly when the network is
# the thing that broke.
#
# The `ia.permission_denied` cause below is the code-page form and carries no
# path at all. The banner form, which substitutes one bank-author-written
# basename, is built by `degraded_banner` in plan 16B-08 per D9. Neither form
# ever carries a resolved absolute path.
HELP_TABLE = {
    "ia.activity_unavailable": {
        "title": "Activity is not available yet",
        "cause": ("Activity isn't available yet in this build. Check back "
                  "after your next update."),
        "next_action": ("Keep using Learn, Practice, Test, and Evidence. "
                        "Nothing else is affected."),
    },
    "ia.agent_unavailable": {
        "title": "Generated help is unavailable",
        "cause": ("Generated help is unavailable. You can keep learning with "
                  "the lesson and authored hints."),
        "next_action": ("Continue the authored loop. Reading, scoring, hints, "
                        "evidence, and reports do not need a model."),
    },
    "ia.cancelled": {
        "title": "You cancelled this",
        "cause": ("Cancelled. Partial results are marked below and were not "
                  "saved as final."),
        "next_action": ("Resume the same operation, or discard the partial "
                        "results explicitly."),
    },
    "ia.course_corrupted": {
        "title": "A course record could not be read",
        "cause": ("This course's full record couldn't be loaded. Showing its "
                  "last valid overview."),
        "next_action": ("Open the last valid overview, or open the course's "
                        "files directly."),
    },
    "ia.crash_recovered": {
        "title": "Your last position was restored",
        "cause": ("Restored your last saved position. Nothing was lost since "
                  "your last saved step."),
        "next_action": "Continue where the resume cue points.",
    },
    "ia.disk_full": {
        "title": "A save could not complete",
        "cause": ("This save could not complete (disk full or interrupted). "
                  "Your previous version is intact. Free up space and try "
                  "again."),
        "next_action": ("Free disk space, then retry the save. The previous "
                        "accepted version stays open and usable meanwhile."),
    },
    "ia.future_schema": {
        "title": "A file came from a newer version",
        "cause": ("This file was saved by a newer version of itembank. The "
                  "parts itembank recognizes are shown below; nothing is "
                  "changed or deleted."),
        "next_action": ("Continue viewing the recognized parts, or update "
                        "itembank to see the rest."),
    },
    "ia.offline": {
        "title": "You are offline",
        "cause": ("You're offline. Reading, practice, scoring, hints, and "
                  "evidence keep working. Anything that needs a network "
                  "connection is marked unavailable below."),
        "next_action": ("Keep working. Nothing local is blocked by being "
                        "offline."),
    },
    "ia.permission_denied": {
        "title": "A folder could not be read",
        "cause": ("itembank could not access a folder it was given. Check "
                  "that the folder is still shared with itembank, then try "
                  "again."),
        "next_action": ("Re-grant access to that folder, or continue with the "
                        "rest of the course, which is unaffected."),
    },
    "ia.route_not_found": {
        "title": "That link does not resolve",
        "cause": ("That address does not name anything itembank can open. The "
                  "thing it pointed at may have been renamed, moved, or "
                  "removed."),
        "next_action": ("Go back to the course overview, or open the course "
                        "shelf and pick the course again."),
    },
    "ia.sample_course_removed": {
        "title": "The sample course was removed",
        "cause": ("The sample course and its bundled files were removed from "
                  "this install."),
        "next_action": ("Bind a source to create your first real course, or "
                        "replay the walkthrough from Help."),
    },
    "ia.walkthrough_unavailable": {
        "title": "The walkthrough could not start",
        "cause": ("The walkthrough content could not be read on this install. "
                  "Everything else works normally."),
        "next_action": ("Use the course shelf directly. The walkthrough can be "
                        "replayed from Help after the next update."),
    },
}


def help_entry(code):
    """One offline help entry for a named error code.

    A pure in-memory lookup: it never reads a file and never opens a socket,
    so it keeps working exactly when connectivity, a hosted model, or a
    configured agent is the thing that broke. An unrecognized code is
    answered with the fallback sentence rather than refused, and no input
    raises, including `None`, an integer, and the empty string.
    """
    if isinstance(code, str) and code in HELP_TABLE:
        row = HELP_TABLE[code]
        return {"code": code, "known": True, "title": row["title"],
                "cause": row["cause"], "next_action": row["next_action"]}
    return {"code": code if isinstance(code, str) else "", "known": False,
            "title": "No help entry yet", "cause": HELP_FALLBACK_COPY,
            "next_action": ""}


def cmd_help_code(a):
    """`itembank help-code <code>` -- the offline help page's CLI twin."""
    print(json.dumps(help_entry(a.code), ensure_ascii=False, indent=2))
    return 0


# The exact empty-shelf copy, from the UI-SPEC Copywriting Contract.
SHELF_EMPTY_HEADING = "No courses yet"
SHELF_EMPTY_BODY = ("Start with the sample course, or bind a source to create "
                    "your first course.")

# Every attention state carries a required text label, so no state is ever
# signalled by color alone.
ATTENTION_COPY = {
    "up_to_date": "Up to date",
    "due": "{N} due",
    "pending_review": "{N} pending review",
    "needs_input": "Needs your input",
    "needs_reconciliation": "Needs reconciliation",
    "last_valid_overview": "Showing last valid overview",
}

# Existing token names assigned by 16B-UI-SPEC. Bare names, no leading dashes,
# no color value; this phase introduces no new visual constant.
ATTENTION_TOKENS = {
    "up_to_date": "ok",
    "due": "warn",
    "pending_review": "warn",
    "needs_input": "warn",
    "needs_reconciliation": "unknown",
    "last_valid_overview": "unknown",
}

# D-16B-10's first sort key: the states that need a human come first, without
# ever synthesizing a score.
ATTENTION_ORDER = ("needs_input", "needs_reconciliation", "pending_review",
                   "due", "last_valid_overview", "up_to_date")

_NO_COURSE_ENV = "ITEMBANK_IA_NO_COURSE"

NOT_STARTED_CUE = "Not started"


def _record_field(record, name, default=None):
    """One field from a course record, reading the landed 14B shape first.

    The landed `course.read_course` returns `{doc, text, fingerprint,
    revision, object_id, state}`; identity is `object_id` and the display name
    is `doc["header"]["title"]`. Attention, counts, a resume cue, and a last
    activity timestamp have no landed source in 14B at all, so they are read
    only when a record carries them and are defaulted otherwise. Reading both
    is one projection over one record, not a second course schema.
    """
    if not isinstance(record, dict):
        return default
    doc = record.get("doc")
    if isinstance(doc, dict):
        header = doc.get("header") or {}
        if name == "course_id":
            return record.get("object_id") or default
        if name == "name":
            return header.get("title") or default
    if name in record and record[name] not in (None, ""):
        return record[name]
    return default


def _attention_of(record):
    """The card's attention state.

    `conflict` is the one attention signal 14B actually records: it is the 14A
    object state the sidecar's registry row carries. Everything else is read
    from the record when present and defaults to up to date, because a state
    nothing recorded is not a state to display.
    """
    if isinstance(record, dict) and record.get("state") == "conflict":
        return "needs_reconciliation"
    declared = _record_field(record, "attention")
    if declared in ATTENTION_STATES and declared != "last_valid_overview":
        return declared
    return "up_to_date"


def _chip_for(attention, record):
    text = ATTENTION_COPY[attention]
    if "{N}" not in text:
        return text
    key = "due_count" if attention == "due" else "pending_review_count"
    count = _record_field(record, key, 0)
    return text.replace("{N}", str(count))


def course_shelf_state(root, course=_UNSET):
    """The course shelf's whole state as a plain dict. Performs no write.

    Passing `course=None` forces the module-absent branch, which is how a
    build without `course.py` behaves; omitting the argument imports `course`
    and falls back to the same branch on `ImportError`, or when
    `ITEMBANK_IA_NO_COURSE` is set to `1`.

    A record that fails to read yields a degraded card built from the
    directory basename and nothing else, never from a partially parsed record
    and never from a resolved absolute path (D9). The one thing known about a
    record that would not parse is that its contents cannot be trusted to be
    safe to display.

    Amended 2026-08-27 by owner ruling (IL-20260827-01), which amended D7: a
    field here may carry a percent character and a card may carry a computed
    ratio. What binds instead is that a ratio is computed only where the
    record supplies both a numerator and a denominator, and where either is
    missing the field reports indeterminate rather than an invented percent. A
    degraded card carries no ratio at all, because its record did not read.

    Amended 2026-08-27, FILE-04 accepted (IL-20260826-01): the set of courses
    belongs to a workspace record, read by pinned `course_object_id`.
    `REQUIREMENTS.md` records FILE-04 as unscheduled and pending, and no
    workspace module exists in this tree, so this function runs FILE-04's
    documented degraded mode: an immediate-subdirectory scan of `root`. A
    sidecar that will not read is a degraded card and is never promoted to a
    course keyed by its folder name, which is the name-based identity FILE-03
    forbids.
    """
    if course is _UNSET:
        if os.environ.get(_NO_COURSE_ENV) == "1":
            _c = None
        else:
            try:
                import course as _c
            except ImportError:
                _c = None
    else:
        _c = course

    empty = {"empty_heading": SHELF_EMPTY_HEADING,
             "empty_body": SHELF_EMPTY_BODY}
    if _c is None:
        result = {"available": False, "cards": []}
        result.update(empty)
        return result

    sidecar = getattr(_c, "COURSE_SIDECAR_FILENAME", "")
    try:
        names = sorted(os.listdir(root))
    except OSError:
        names = []

    cards = []
    for entry in names:
        course_dir = os.path.join(root, entry)
        if not os.path.isdir(course_dir):
            continue
        if not os.path.exists(os.path.join(course_dir, sidecar)):
            continue
        try:
            record = _c.read_course(course_dir)
        except Exception:
            cards.append(_degraded_card(os.path.basename(course_dir)))
            continue
        cards.append(_healthy_card(record, os.path.basename(course_dir)))

    cards.sort(key=_shelf_sort_key)
    result = {"available": True, "cards": cards}
    result.update(empty)
    return result


def _healthy_card(record, basename):
    course_id = _record_field(record, "course_id", basename)
    name = _record_field(record, "name", basename)
    attention = _attention_of(record)
    cue = _record_field(record, "resume_cue", NOT_STARTED_CUE)
    verb = "Start " if cue == NOT_STARTED_CUE else "Resume "
    return {
        "course_id": course_id,
        "name": name,
        "attention": attention,
        "chip": _chip_for(attention, record),
        "token": ATTENTION_TOKENS[attention],
        "resume_cue": cue,
        "cta_label": verb + name,
        "cta_href": "/course/" + course_id,
        "degraded": False,
        "help_code": None,
        "actions": (),
        "last_activity": _record_field(record, "last_activity"),
    }


def _degraded_card(basename):
    """A card for a record that would not read. Built from the directory
    basename only, so nothing from an untrusted record reaches a page, and it
    still offers two real ways forward rather than being a dead end."""
    return {
        "course_id": basename,
        "name": basename,
        "attention": "last_valid_overview",
        "chip": ATTENTION_COPY["last_valid_overview"],
        "token": ATTENTION_TOKENS["last_valid_overview"],
        "resume_cue": "Showing last valid overview",
        "cta_label": "Open last valid overview",
        "cta_href": "/course/" + basename,
        "degraded": True,
        "help_code": "ia.course_corrupted",
        "actions": ({"label": "Open last valid overview",
                     "href": "/course/" + basename},
                    {"label": "View files",
                     "href": "/course/" + basename + "/sources"}),
        "last_activity": None,
    }


def _shelf_sort_key(card):
    """D-16B-10's total order: attention rank, then most recent activity
    descending with a missing timestamp last, then course id ascending."""
    rank = ATTENTION_ORDER.index(card["attention"])
    stamp = card["last_activity"]
    return (rank, stamp is None, _descending(stamp), card["course_id"])


def _descending(stamp):
    """Sort an ISO timestamp string newest-first inside an ascending sort, by
    inverting each character's code point against a fixed ceiling."""
    if not isinstance(stamp, str):
        return ()
    return tuple(-ord(ch) for ch in stamp)


# Each area's exact Chrome-voice nav label, from the UI-SPEC Course level table.
COURSE_AREA_LABELS = {
    "overview": "Overview",
    "learn": "Learn",
    "practice": "Practice",
    "test": "Test",
    "map": "Course map",
    "sources": "Sources",
    "build": "Build and review",
    "agent": "Agent",
    "evidence": "Evidence",
}

AREA_NOT_FOUND_NOTICE = "That address does not name anything itembank can open."
ANCHOR_NOT_FOUND_NOTICE = ("The part of this page that link pointed at is no "
                           "longer here. The rest of the page is below.")

# A course-area state is presentation-only. It gives every degraded branch a
# distinct label and one existing, safe way forward without inventing progress,
# changing the addressed course, or making a second session authority.
COURSE_AREA_STATES = {
    "empty": {"notice": "Nothing has been added to {area_label} for this course yet.", "action_label": "Return to course overview"},
    "loading": {"notice": "Loading {area_label}. The last accepted course state remains available.", "action_label": "Return to course overview"},
    "unavailable": {"notice": "{area_label} is unavailable right now. Local course material remains available.", "action_label": "Read offline help", "action_href": "/help/ia.offline"},
    "conflict": {"notice": "This course changed while you were away. Nothing was overwritten.", "action_label": "Inspect current course"},
    "interrupted": {"notice": "Your work was interrupted. Resume the same session from its saved position.", "action_label": "Resume this area"},
    "pending": {"notice": "Your response is recorded and pending review. No mark is implied.", "action_label": "Continue course"},
    "invalid": {"notice": "The saved presentation profile is unsupported. A safe fallback is active.", "action_label": "Save a supported profile", "action_href": "/settings"},
    "recovery": {"notice": "The last accepted course state is still available. Retry from that state.", "action_label": "Retry from last accepted state"},
}


def course_area_notice(course_id, area, state="empty"):
    """Return a visible course-area state and its one supported next action.

    The caller supplies no mutable runtime data. This makes the transition and
    degraded-state matrix fixtureable while leaving session cursor, evidence,
    and disclosure decisions in their existing owners.
    """
    if area not in COURSE_AREAS:
        raise ValueError("unknown course area: %s" % area)
    spec = COURSE_AREA_STATES.get(state)
    if spec is None:
        raise ValueError("unknown course-area state: %s" % state)
    return {"state": state,
            "notice": spec["notice"].format(area_label=COURSE_AREA_LABELS[area]),
            "action_label": spec["action_label"],
            "action_href": spec.get("action_href") or "/course/" + course_id}


def anchor_slug(text):
    """The anchor id for one heading.

    A named alias for `model.lesson_slug` so callers read intent. There is
    exactly one slug implementation in this repository, and a second one here
    would create a second anchor vocabulary: a lookup that agrees with an
    anchor by coincidence eventually disagrees.
    """
    return model.lesson_slug(text)


def deep_link_target(course_id, area=None, lesson_id=None, anchor=None,
                     course_name=None):
    """The addressable target one deep link names, as a plain dict.

    The path segment is always the opaque `course_id`, never a display name,
    so a renamed course keeps every saved link it had. Raises nothing: an area
    outside `COURSE_AREAS` returns `area` None and the Overview path, and the
    caller decides whether that is a 404.
    """
    name = course_name or course_id
    if lesson_id:
        return {"path": "/course/%s/learn/%s" % (course_id, lesson_id),
                "area": "learn", "label": COURSE_AREA_LABELS["learn"],
                "back_href": "/course/" + course_id,
                "back_label": "Back to " + name,
                "anchor": anchor_slug(anchor) if anchor else None}
    if area in (None, "overview"):
        return {"path": "/course/" + course_id, "area": "overview",
                "label": COURSE_AREA_LABELS["overview"],
                "back_href": "/", "back_label": "Back to courses",
                "anchor": anchor_slug(anchor) if anchor else None}
    if area not in COURSE_AREAS:
        return {"path": "/course/" + course_id, "area": None,
                "label": COURSE_AREA_LABELS["overview"],
                "back_href": "/", "back_label": "Back to courses",
                "anchor": anchor_slug(anchor) if anchor else None}
    return {"path": "/course/%s/%s" % (course_id, area), "area": area,
            "label": COURSE_AREA_LABELS[area],
            "back_href": "/course/" + course_id,
            "back_label": "Back to " + name,
            "anchor": anchor_slug(anchor) if anchor else None}


def course_dir_for(root, course_id, module=None):
    """The directory this course lives in, or None.

    The public name for the resolution `course_area_state` already does, so
    a surface that wants to read the course's own artifacts resolves the
    directory the same way the frame does rather than inventing a second
    rule (`17B-03 D-06 item 3`, the empty course areas).
    """
    if module is None:
        try:
            import course as module
        except ImportError:
            return None
    return _course_dir_for(root, course_id, module)


def _course_dir_for(root, course_id, module):
    """The directory whose sidecar names `course_id`, or the directory whose
    basename is `course_id` when no sidecar claims it.

    Identity is the pinned `course_object_id` first (FILE-03), and the
    basename only as the degraded fallback a card that could not read its
    record already declares.
    """
    sidecar = getattr(module, "COURSE_SIDECAR_FILENAME", "")
    try:
        names = sorted(os.listdir(root))
    except OSError:
        return None
    fallback = None
    for entry in names:
        path = os.path.join(root, entry)
        if not os.path.isdir(path):
            continue
        if not os.path.exists(os.path.join(path, sidecar)):
            continue
        if entry == course_id:
            fallback = path
        try:
            record = module.read_course(path)
        except Exception:
            continue
        if _record_field(record, "course_id") == course_id:
            return path
    return fallback


def course_area_state(root, course_id, area, course=_UNSET,
                      display_state="empty"):
    """One course area's whole frame as a plain dict. Performs no write.

    `content_available` is False for every area in this phase: the record
    shapes that fill an area belong to Phases 14A and 14B, so the area states
    what it holds rather than rendering a blank region or claiming content it
    does not have. The nav is always all eight areas in `COURSE_AREAS` order,
    at every layout width, because layout is a rendering decision inside the
    handler and never a second URL for the same object.
    """
    if course is _UNSET:
        if os.environ.get(_NO_COURSE_ENV) == "1":
            _c = None
        else:
            try:
                import course as _c
            except ImportError:
                _c = None
    else:
        _c = course

    missing = {"found": False, "course_id": course_id, "course_name": course_id,
               "area": None, "area_label": "", "nav": [],
               "notice": AREA_NOT_FOUND_NOTICE,
               "help_code": "ia.route_not_found", "content_available": False}

    if _c is None or area not in COURSE_AREAS:
        return missing

    course_dir = _course_dir_for(root, course_id, _c)
    if course_dir is None:
        return missing

    try:
        record = _c.read_course(course_dir)
    except Exception:
        record = None
    basename = os.path.basename(course_dir)
    name = _record_field(record, "name", basename) if record else basename

    nav = []
    for member in COURSE_AREAS:
        target = deep_link_target(course_id, member, course_name=name)
        nav.append({"area": member, "label": COURSE_AREA_LABELS[member],
                    "href": target["path"], "current": member == area})

    label = COURSE_AREA_LABELS[area]
    display = course_area_notice(course_id, area, display_state)
    return {"found": True, "course_id": course_id, "course_name": name,
            "area": area, "area_label": label, "nav": nav,
            "notice": display["notice"], "display_state": display["state"],
            "next_action": {"label": display["action_label"],
                            "href": display["action_href"]},
            "help_code": None, "content_available": False}


# The seven mode layers as data, built by iterating MODE_LAYERS so exactly one
# ordering exists in this module. `fixed` is True for exactly the two members
# of MODE_LAYERS_FIXED: those two are never configurable, during a sitting or
# outside one.
_MODE_LAYER_TEXT = {
    "learner_preference": (
        "Learner preference",
        "You, reversible at any safe transition",
        "Reader or guided view, allowed note strategy, choose another next "
        "action"),
    "author_strategy": (
        "Author or course strategy",
        "The course builder, within the registered catalog",
        "Authored sequence, required artifact, direct-reading treatment"),
    "objective_constraint": (
        "Objective constraint",
        "The objective and blueprint authority",
        "Cognitive demand, required construct, permitted evidence"),
    "accommodation_override": (
        "Accommodation override",
        "Your stated need, or the assigning authority",
        "Equivalent input or output, pace, reduced motion"),
    "instructor_policy": (
        "Instructor policy",
        "The assigning authority for a bounded course",
        "Required path, deadline, formal completion predicate"),
    "runtime_authority": (
        "Runtime authority",
        "Fixed by itembank, never configurable during a sitting",
        "Scoring, keyed disclosure, retries, formal-test pause"),
    "system_safety": (
        "System safety",
        "Fixed by itembank",
        "Permission scope, rights and egress checks, no authored-script "
        "authority"),
}

MODE_LAYER_ROWS = tuple(
    {"layer": layer, "label": _MODE_LAYER_TEXT[layer][0],
     "controller": _MODE_LAYER_TEXT[layer][1],
     "example": _MODE_LAYER_TEXT[layer][2],
     "fixed": layer in MODE_LAYERS_FIXED}
    for layer in MODE_LAYERS)

MODE_LAYER_FIXED_HEADING = "Always fixed by itembank"

# `{layer}` is substituted with a display phrase, never an internal key, so the
# sentence reads as English. The UI-SPEC's own worked example, verbatim:
# Timed test mode is set by your instructor's policy and can't be changed here.
MODE_LAYER_CONFLICT_TEMPLATE = ("{setting} is set by {layer} for this course "
                                "and can't be changed here.")

# The phrase that reads correctly inside MODE_LAYER_CONFLICT_TEMPLATE.
MODE_LAYER_DISPLAY_PHRASES = {
    "learner_preference": "your own preference",
    "author_strategy": "this course's design",
    "objective_constraint": "this objective's requirements",
    "accommodation_override": "your accommodation settings",
    "instructor_policy": "your instructor's policy",
    "runtime_authority": "itembank's assessment rules",
    "system_safety": "itembank's safety rules",
}


def mode_layer_rows():
    """The seven layers as shallow copies, so a caller cannot mutate the
    module constant."""
    return [dict(row) for row in MODE_LAYER_ROWS]


def mode_layer_conflict_copy(setting_name, layer):
    """The exact locked sentence for one refused control. Raises `KeyError`
    for an unknown layer rather than emitting a sentence naming nothing."""
    return MODE_LAYER_CONFLICT_TEMPLATE.format(
        setting=setting_name, layer=MODE_LAYER_DISPLAY_PHRASES[layer])


def mode_layer_resolve(setting_name, requests):
    """The pure half of the mode-layer contract.

    It reads only its two arguments. It imports no strategy, accommodation, or
    instructor record and touches no file. The collector that populates
    `requests` from live state is Phase 16C's under D8 and D-16B-12, so there
    is one precedence rule in this repository and not two.

    The winning layer is the highest-indexed member of `MODE_LAYERS` present
    in `requests`. An unknown key raises `ValueError` rather than being
    ignored, because silently dropping a layer would let a caller believe its
    request was considered.
    """
    for key in requests:
        if key not in MODE_LAYERS:
            raise ValueError("unknown mode layer: %r" % key)

    present = [layer for layer in MODE_LAYERS if layer in requests]
    if not present:
        return {"value": None, "winning_layer": None, "conflict": False,
                "copy": ""}

    winner = present[-1]
    value = requests[winner]
    conflict = any(requests[layer] != value for layer in present[:-1])
    return {"value": value, "winning_layer": winner, "conflict": conflict,
            "copy": (mode_layer_conflict_copy(setting_name, winner)
                     if conflict else "")}


# The exact Degraded-State Matrix sentence for each state. `permission_denied`
# is the only row carrying a substitution, and `{target}` is always passed
# through `os.path.basename` per D9, reusing the shipped `lesson.src_unreadable`
# precedent. The `agent_unavailable` sentence is a LOCKED string from the
# project-level UI-SPEC Copywriting contract and is never re-worded.
DEGRADED_COPY = {
    "crash": ("Restored your last saved position. Nothing was lost since your "
              "last saved step."),
    "cancelled": ("Cancelled. Partial results are marked below and were not "
                  "saved as final."),
    "disk_full": ("This save could not complete (disk full or interrupted). "
                  "Your previous version is intact. Free up space and try "
                  "again."),
    "offline": ("You're offline. Reading, practice, scoring, hints, and "
                "evidence keep working. Anything that needs a network "
                "connection is marked unavailable below."),
    "permission_denied": ("itembank could not access {target}. Check that the "
                          "folder is still shared with itembank, then try "
                          "again."),
    "future_schema": ("This file was saved by a newer version of itembank. The "
                      "parts itembank recognizes are shown below; nothing is "
                      "changed or deleted."),
    "agent_unavailable": ("Generated help is unavailable. You can keep "
                          "learning with the lesson and authored hints."),
    "course_corrupted": ("This course's full record couldn't be loaded. "
                         "Showing its last valid overview."),
}

# The Degraded-State Matrix's "Next safe action offered" column. Every list is
# non-empty, which makes the expose-the-next-safe-action half of the contract
# structural rather than a habit.
DEGRADED_ACTIONS = {
    "crash": ({"label": "Continue where you left off", "href": "/"},),
    "cancelled": ({"label": "Resume this operation", "href": "/activity"},
                  {"label": "Discard the partial results", "href": "/activity"}),
    "disk_full": ({"label": "Try the save again", "href": "/"},),
    "offline": ({"label": "Keep working offline", "href": "/"},),
    "permission_denied": ({"label": "Re-grant access", "href": "/settings"},
                          {"label": "Continue with the rest of the course",
                           "href": "/"}),
    "future_schema": ({"label": "Continue with the recognized parts",
                       "href": "/"},),
    "agent_unavailable": ({"label": "Continue the authored loop", "href": "/"},),
    "course_corrupted": ({"label": "Open last valid overview", "href": "/"},
                         {"label": "View files", "href": "/"}),
}

# Every value here must be a member of IA_HELP_CODES and a key of HELP_TABLE.
# `check_banner_help_links_resolve` asserts that as a mapping over the tuple,
# so a state added without a help page fails rather than linking nowhere.
DEGRADED_HELP_CODES = dict(
    (state, "ia.crash_recovered" if state == "crash" else "ia." + state)
    for state in DEGRADED_STATES)

DEGRADED_TOKEN = "unknown"


def degraded_banner(state, target=None, course_id=None):
    """One degraded-state banner as a plain dict. Renders nothing itself.

    `{target}` is always reduced to a basename per D9, so no resolved absolute
    path reaches a page. The token is always `unknown` because no degraded
    state is a learner error: none of these eight is something the learner did
    wrong, and colouring them as an error would say otherwise.
    """
    if state not in DEGRADED_STATES:
        raise ValueError("unknown degraded state: %r" % state)

    text = DEGRADED_COPY[state]
    if state == "permission_denied":
        basename = os.path.basename(
            str(target or "").replace("\\", "/").rstrip("/"))
        text = text.replace("{target}", basename)

    code = DEGRADED_HELP_CODES[state]
    actions = [dict(action) for action in DEGRADED_ACTIONS[state]]
    if state == "course_corrupted" and course_id:
        actions[0]["href"] = "/course/" + course_id
        actions[1]["href"] = "/course/" + course_id + "/sources"
    actions.append({"label": "Read more about this", "href": "/help/" + code})

    return {"state": state, "text": text, "code": code,
            "token": DEGRADED_TOKEN, "actions": actions}


def degraded_banner_for(states, **kw):
    """The banner for the first member of `DEGRADED_STATES` present in
    `states`, plus `also_fired`, the help codes of every other fired state.

    This is D-16B-9's deterministic precedence read straight off the declared
    tuple. There is no second ordering anywhere: the banner slot is won by
    tuple order and every other fired state stays reachable through its own
    help link.
    """
    fired = [state for state in DEGRADED_STATES if state in set(states)]
    if not fired:
        return None
    banner = degraded_banner(fired[0], **kw)
    banner["also_fired"] = [DEGRADED_HELP_CODES[s] for s in fired[1:]]
    return banner


LOCKED_CARD_HEADER_TEMPLATE = "{name}, locked"
LOCKED_CARD_TEMPLATE = "Unlocks after {condition}."

# A refusal payload with no stated condition must still render a stated
# condition, never a blank card and never the fragment "Unlocks after .". This
# exact substitute sentence is plan 16B-08's own and is carried as a backstop
# row until the runtime's real refusal payload shape is known.
LOCKED_CARD_NO_CONDITION = "Unlocks after the next authored step."


def locked_refusal_card(name, condition="", affordance=None):
    """One locked refusal card as a plain dict. Renders nothing itself.

    This is the general form of the shipped RTS-09 locked hint tier,
    generalized to the Socratic refusal FLOW-02 names. It carries none of the
    content it withholds: the function accepts no parameter that could hold
    that content, so what is withheld is absent from the bytes rather than
    hidden inside them. The unlock condition is computed by the runtime and
    passed in; a model never selects it, and a model arguing for a reveal
    still cannot produce one, because the reveal is not this function's to
    make.
    """
    stated = (condition or "").strip()
    body = (LOCKED_CARD_TEMPLATE.format(condition=stated.rstrip("."))
            if stated else LOCKED_CARD_NO_CONDITION)
    single = None
    if isinstance(affordance, dict):
        single = {"label": affordance.get("label", ""),
                  "href": affordance.get("href", "")}
    return {"header": LOCKED_CARD_HEADER_TEMPLATE.format(name=name),
            "body": body, "condition": stated, "affordance": single}


IA_STATE_DIR = "_ia"

# Per-install app state, not learner preferences and not evidence. Putting
# these in `itembank.json` would mix app state into a published settings
# contract; putting them in the evidence store would create a second writer
# over it (D-16B-5).
IA_STATE_DEFAULTS = {
    "walkthrough": {"status": "unseen", "step": 0},
    "sample_course": {"removed": False},
}


def _ia_state_path(root, name):
    return os.path.join(root, IA_STATE_DIR, name + ".json")


def read_ia_state(root, name):
    """One `_ia/<name>.json` record, merged under its default.

    A missing file, an unreadable file, a non-object JSON value, and a decode
    error all return the plain default and raise nothing, and none of them
    creates a file. A truncated record is the ordinary outcome of a fault
    during a write, so it reads as the default rather than as an error.
    """
    state = dict(IA_STATE_DEFAULTS[name])
    try:
        with open(_ia_state_path(root, name), "r", encoding="utf-8") as fh:
            stored = json.load(fh)
    except (OSError, ValueError):
        return state
    if isinstance(stored, dict):
        state.update(stored)
    return state


def write_ia_state(root, name, data):
    """One `_ia/<name>.json` record, written atomically.

    Copies `runtime.write_session`'s shape exactly: write to a temporary path
    beside the target, then `os.replace`. A fault during the write leaves
    either the old file or the new file and never a half-written one, and no
    temporary file is left behind on success.
    """
    directory = os.path.join(root, IA_STATE_DIR)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    final = _ia_state_path(root, name)
    staged = final + ".tmp"
    with open(staged, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(data, indent=2, ensure_ascii=False))
        fh.flush()
    os.replace(staged, final)
    return final


WALKTHROUGH_COPY = {
    "offer": "New here? A short walkthrough shows how a course works.",
    "start": "Start walkthrough",
    "skip": "Skip for now",
    "replay": "Replay walkthrough",
}

SAMPLE_COURSE_COPY = {
    "card_note": "For exploring itembank. Remove it anytime.",
    "remove": "Remove sample course",
    "confirm": ("Remove this sample course? This deletes its bundled files "
                "and cannot be undone."),
}

# Every href is a real route this phase registered, so there is no separate
# tour-mode route and no second URL for a page the shelf already addresses.
WALKTHROUGH_STEPS = (
    {"href": "/", "title": "Your courses live here",
     "body": "Every course you build or bind shows up on this shelf with what "
             "it needs from you next."},
    {"href": "/course/" + sample_course.SAMPLE_COURSE_ID,
     "title": "A course overview",
     "body": "Overview says what this course is for and what to do next. "
             "Learn, Practice, Test, and Evidence are one click away."},
    {"href": "/course/" + sample_course.SAMPLE_COURSE_ID + "/learn",
     "title": "Reading and lessons",
     "body": "Learn holds readings and lessons. Reading is continuous and "
             "scrolls; nothing is split across pages."},
    {"href": "/settings", "title": "Settings, and what is fixed",
     "body": "Settings covers approved roots, model backends, network and "
             "sharing, accessibility, storage, and updates. It also shows what "
             "itembank always decides for itself."},
)

SHELF_ACTIONS = ("add_sample_course", "advance_walkthrough", "remove_sample_course",
                 "replay_walkthrough", "skip_walkthrough")


def walkthrough_state(root):
    """The walkthrough's whole state. The offer shows only while the status is
    unseen; the replay control is available at every status, so skipping is
    never a lost opportunity."""
    stored = read_ia_state(root, "walkthrough")
    step = stored.get("step")
    if not isinstance(step, int) or step < 0:
        step = 0
    index = min(step, len(WALKTHROUGH_STEPS) - 1)
    return {"status": stored.get("status", "unseen"), "step": step,
            "total": len(WALKTHROUGH_STEPS),
            "offer_copy": WALKTHROUGH_COPY["offer"],
            "start_copy": WALKTHROUGH_COPY["start"],
            "skip_copy": WALKTHROUGH_COPY["skip"],
            "replay_copy": WALKTHROUGH_COPY["replay"],
            "current": dict(WALKTHROUGH_STEPS[index])}


def sample_course_state(root):
    """Whether the bundled sample course is on disk and whether it was
    removed. `present` is a filesystem fact; `removed` is the recorded
    decision, so a re-materialization cannot quietly undo a removal."""
    stored = read_ia_state(root, "sample_course")
    directory = os.path.join(root, sample_course.SAMPLE_COURSE_DIRNAME)
    return {"present": os.path.isdir(directory),
            "removed": bool(stored.get("removed")),
            "course_id": sample_course.SAMPLE_COURSE_ID,
            "name": sample_course.SAMPLE_COURSE_NAME,
            "note": SAMPLE_COURSE_COPY["card_note"],
            "remove_label": SAMPLE_COURSE_COPY["remove"],
            "confirm_copy": SAMPLE_COURSE_COPY["confirm"]}


def apply_shelf_action(root, action):
    """Apply one shelf or first-run action and return what happened.

    The only path this function ever deletes is `root` joined with
    `sample_course.SAMPLE_COURSE_DIRNAME`. No path from a request reaches it,
    which is why the route can accept exactly one field.
    """
    if action not in SHELF_ACTIONS:
        raise ValueError("unknown shelf action: %r" % action)

    if action == "add_sample_course":
        directory = os.path.join(root, sample_course.SAMPLE_COURSE_DIRNAME)
        written = sample_course.write_sample_course(directory)
        state = {"removed": False}
        write_ia_state(root, "sample_course", state)
        return {"action": action, "ok": True,
                "message": "The sample course is ready.",
                "written": len(written), "state": state}

    if action == "skip_walkthrough":
        state = {"status": "skipped", "step": read_ia_state(
            root, "walkthrough").get("step", 0)}
        write_ia_state(root, "walkthrough", state)
        return {"action": action, "ok": True,
                "message": "Walkthrough skipped.", "state": state}

    if action == "replay_walkthrough":
        state = {"status": "in_progress", "step": 0}
        write_ia_state(root, "walkthrough", state)
        return {"action": action, "ok": True,
                "message": "Walkthrough restarted.", "state": state}

    if action == "advance_walkthrough":
        stored = read_ia_state(root, "walkthrough")
        step = stored.get("step")
        if not isinstance(step, int) or step < 0:
            step = 0
        state = {"status": "in_progress",
                 "step": min(step + 1, len(WALKTHROUGH_STEPS) - 1)}
        write_ia_state(root, "walkthrough", state)
        return {"action": action, "ok": True,
                "message": "Moved to step %d of %d."
                           % (state["step"] + 1, len(WALKTHROUGH_STEPS)),
                "state": state}

    stored = read_ia_state(root, "sample_course")
    directory = os.path.join(root, sample_course.SAMPLE_COURSE_DIRNAME)
    if stored.get("removed") and not os.path.isdir(directory):
        return {"action": action, "ok": True,
                "message": "The sample course was already removed. Nothing "
                           "to do.",
                "state": dict(stored)}
    leftover = []
    if os.path.isdir(directory):
        leftover = _remove_sample_dir(directory)
    state = {"removed": True}
    write_ia_state(root, "sample_course", state)
    if leftover:
        return {"action": action, "ok": True,
                "message": "The sample course's bundled files were removed. "
                           "Its folder was kept because it still contains: "
                           + ", ".join(leftover) + ".",
                "state": state}
    return {"action": action, "ok": True,
            "message": "The sample course and its bundled files were removed.",
            "state": state}


def _remove_sample_dir(directory):
    """Delete the materialized sample course and report what survived.

    Deliberately not a recursive tree delete. It removes the directory's own
    files, prunes any subdirectory that is already empty (the daemon creates
    an empty `_attempts/` inside any root it serves, which is debris rather
    than learner data), and then removes the directory itself.

    Anything else, a non-empty subtree or a subdirectory it could not prune,
    is left exactly where it is and its name is returned, so the caller
    reports what actually happened rather than claiming a removal that did
    not occur.
    """
    leftover = []
    for entry in sorted(os.listdir(directory)):
        path = os.path.join(directory, entry)
        if os.path.isfile(path) or os.path.islink(path):
            os.unlink(path)
            continue
        try:
            os.rmdir(path)
        except OSError:
            leftover.append(entry)
    if leftover:
        return leftover
    try:
        os.rmdir(directory)
    except OSError as exc:
        return [str(exc)]
    return []


def cmd_shelf(a):
    """`itembank shelf <action> <dir>` -- the POST /api/shelf CLI twin."""
    print(json.dumps(apply_shelf_action(a.dir, a.action),
                     ensure_ascii=False, indent=2))
    return 0


# The seven end-to-end loops, transcribed verbatim from the 16B-UI-SPEC Core
# Loop Resume Contract table and from nowhere else. No step is paraphrased,
# reordered, merged, or split: the table is the contract and this is its
# machine-readable form. Counts per loop are A 9, B 9, C 9, D 8, E 6, F 9,
# G 9, for 59 steps in total.
LOOP_STEPS = {
    "A": {
        "title": "discover, reconcile, bind",
        "steps": (
            "declare read roots and rights",
            "scan read-only",
            "identify by stable ID plus fingerprint",
            "preview and classify",
            "surface duplicates/moves/conflicts/unsupported",
            "choose link/import/copy/move/ignore",
            "bind to objectives",
            "validate",
            "checkpoint and index",
        ),
        "resume_unit": "last completed step, keyed to the discovery run's own ID",
    },
    "B": {
        "title": "design a course",
        "steps": (
            "establish target/scope",
            "import or draft graph",
            "separate outline from prerequisites",
            "map sources/artifacts",
            "classify coverage",
            "choose treatment per objective",
            "define paths/completion",
            "review gaps/conflicts",
            "accept a versioned plan",
        ),
        "resume_unit": "the objective or treatment decision in progress",
    },
    "C": {
        "title": "learn and construct notes",
        "steps": (
            "resume with objective and rationale",
            "orient",
            "read/observe/predict/manipulate/explain/construct",
            "optionally capture notes",
            "inspect citation",
            "perform a check",
            "receive feedback",
            "transfer in changed context",
            "save position/next action",
        ),
        "resume_unit": "exact lesson position (anchor) plus activity attempt state",
    },
    "D": {
        "title": "practice and test",
        "steps": (
            "choose practice or enter a fixed test",
            "runtime provides public item",
            "learner responds",
            "runtime records/scores or marks pending",
            "runtime grants the permitted feedback tier",
            "practice may remediate/retry",
            "test preserves formal conditions",
            "report separates settled/pending/unknown/omitted",
        ),
        "resume_unit": "session cursor (existing shipped session contract, unchanged)",
    },
    "E": {
        "title": "evidence and remediation",
        "steps": (
            "replay a named evidence snapshot",
            "show scope/denominator/window/pending/unknown/uncertainty",
            "explain a recommended next action",
            "learner accepts/chooses another/overrides",
            "revisit prerequisite/explanation/example/transfer/retrieval",
            "append new evidence",
        ),
        "resume_unit": "the evidence snapshot ID last viewed",
    },
    "F": {
        "title": "author, review, accept",
        "steps": (
            "declare objective/treatment/sources/scope/authority",
            "discover existing work",
            "draft smallest missing artifact",
            "record provenance/fallbacks",
            "parse/lint/render/test",
            "show bounded diff/consequences/undo",
            "accept/reject/revise",
            "publish",
            "mark derivatives stale/rebuild",
        ),
        "resume_unit": "the draft or diff under review",
    },
    "G": {
        "title": "maintain, recover, leave",
        "steps": (
            "detect external/source/version change",
            "mark affected bindings/proposals stale",
            "compare base/current/proposal",
            "rebind/migrate/supersede/retain",
            "write atomically with journal",
            "validate",
            "export package/loss report",
            "restore on a clean machine",
            "rebuild disposable state",
        ),
        "resume_unit": "the pending stale/conflict item, or the export/restore job",
    },
}


# The next-action copy patterns from the same table, verbatim and in order.
# Loop D's "Resume practice" and "Start practice" and loop E's "Review
# evidence" are LOCKED strings reused from the project-level UI-SPEC
# Copywriting contract; they are never re-worded here or anywhere else.
LOOP_NEXT_ACTION = {
    "A": ("Continue discovery: {N} files not yet reviewed", "Resolve {N} conflicts before binding"),
    "B": ("Continue course design: {N} objectives still need a treatment",),
    "C": ("Resume {course name}", "Continue reading: {heading}"),
    "D": ("Resume practice", "Start practice"),
    "E": ("Review evidence",),
    "F": ("Continue draft review: {N} findings to resolve",),
    "G": ("Resolve {N} stale item(s)", "Continue restore"),
}


# What an empty run of each loop produced. This plan's own copy, written to
# satisfy the FLOW-01 empty edge: not one of the seven is a blank state, and
# each names a real outcome and a real next move rather than reporting an
# absence.
LOOP_EMPTY_OUTCOME = {
    "A": ("Nothing new was found in the roots you approved. Approve another "
          "root, or continue with what is already bound."),
    "B": ("This course has no objectives yet, so there is nothing to give a "
          "treatment. Add or import objectives to continue."),
    "C": ("There is nothing left to read in this course right now. Practice "
          "what you have read, or add a source."),
    "D": ("Nothing is due for practice right now. Read something new, or "
          "practice ahead of schedule."),
    "E": ("No evidence has been recorded for this course yet. Complete one "
          "activity and a snapshot becomes available."),
    "F": ("Nothing is waiting for review. Draft a treatment, or continue "
          "reading."),
    "G": ("Nothing is stale and nothing needs a decision. Export a backup, or "
          "continue where you left off."),
}

# The stable primary key for `resumable_loops`.
LOOP_ORDER = ("A", "B", "C", "D", "E", "F", "G")


def loop_resume_state(loop, completed_step, item_count=None):
    """One loop's resume position as a plain dict.

    Reads only its arguments and no durable record. The route handlers already
    compute resume cues from evidence and, once it lands, the journal; a second
    resume authority here would compete with them rather than serve them.

    A loop interrupted exactly at a step boundary resumes at that boundary,
    with the following step as the next justified action. A completed loop and
    an empty loop both still owe a next action, so `next_action` is never
    empty.
    """
    if loop not in LOOP_STEPS:
        raise ValueError("unknown loop: %r" % loop)
    steps = LOOP_STEPS[loop]["steps"]
    if not isinstance(completed_step, int) or completed_step < 0:
        completed_step = 0
    completed_step = min(completed_step, len(steps))
    at_end = completed_step == len(steps)
    empty = item_count == 0
    return {
        "loop": loop,
        "title": LOOP_STEPS[loop]["title"],
        "completed_step": completed_step,
        "next_step": None if at_end else steps[completed_step],
        "resume_unit": LOOP_STEPS[loop]["resume_unit"],
        "at_end": at_end,
        "empty": empty,
        "outcome": LOOP_EMPTY_OUTCOME[loop] if empty else "",
        "next_action": LOOP_NEXT_ACTION[loop][0],
    }


def resumable_loops(entries):
    """Loop positions in one total order: `LOOP_ORDER` index, then most recent
    activity descending with a missing timestamp last, then course id
    ascending.

    The course-id final tiebreak is the same rule D-16B-10 locked for the
    course shelf, so this repository has one tiebreak rule and not two.
    """
    def key(entry):
        loop = entry.get("loop")
        rank = LOOP_ORDER.index(loop) if loop in LOOP_ORDER else len(LOOP_ORDER)
        stamp = entry.get("last_activity")
        return (rank, stamp is None, _descending(stamp),
                entry.get("course_id") or "")
    return sorted(entries, key=key)


def cmd_activity(a):
    """`itembank activity <dir>` -- the Activity view's CLI twin. Prints the
    same read model the route renders, and writes nothing."""
    print(json.dumps(activity_view_state(a.dir), ensure_ascii=False, indent=2))
    return 0
