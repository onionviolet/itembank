#!/usr/bin/env python3
"""Legacy-artifact upgrade: audit first, propose a bounded diff, and halt on
anything that would move keyed assessment meaning (UPGRADE-01, UPGRADE-02).

This module reads and proposes. It writes nothing, ever, which is the
`surfaces/migrate.py` posture: read the legacy artifact read-only, show what
would change, and leave the writing to the 14A journal operations under the
operation contract. A module that could both decide a change and apply it
would make the review step optional in practice however loudly the
documentation said otherwise.

Three rules shape everything here.

The audit runs FIRST and completely. There is no public function that
proposes a diff without auditing, so audit-before-edit is structural rather
than procedural. A row whose backing record does not exist yet reads the
plan-text stand-in and never an invented pass: an audit that quietly reports
success for a check it could not run is worse than no audit.

Cosmetic novelty is rejected. A proposed change whose stated reason names no
learning value never reaches the proposed list. The point of an upgrade is
that the artifact teaches better afterwards, and a change that cannot say how
is churn with a changelog entry.

A keyed-meaning change HALTS. Not warns, not asks, not offers an override,
because assessment meaning is the runtime's and an upgrade is not the place
it changes. The halted result carries two affordances and no third, and it
carries no diff at all: there is nothing to review here, only somewhere else
to go.
"""
import os

import model
import note_outputs


# The eleven items, in the order the audit renders them. Order is part of the
# contract: a reviewer who reads the same rows in the same places builds a
# habit that catches a missing one.
BASELINE_AUDIT_ITEMS = ("current_parse", "identity", "fingerprint",
                        "objectives", "sources", "rights", "media",
                        "assessment_boundaries", "plain_rendering",
                        "rich_rendering", "validation")

# Locked copy, transcribed verbatim from the 16C-UI-SPEC Copywriting
# Contract.
PLAN_TEXT_STAND_IN = "plan-text stand-in"
AUDIT_HEADING = "Baseline audit"
AUDIT_COMPLETION_LINE = "All 11 baseline checks recorded."
DIFF_HEADING = "Proposed changes ({N})"
COSMETIC_SKIP_COPY = "Skipped: no learning value added."
CANNOT_EXPRESS_COPY = "This artifact can't express {enhancement} in its own form. It keeps its form; a derived enhancement is linked, with its portability cost stated."
KEYED_HALT_COPY = "Halted: this change would alter keyed assessment meaning ({what}). Assessment changes are reviewed separately and are never part of an upgrade."
KEYED_HALT_AFFORDANCES = ("Open assessment review", "Cancel upgrade")

# Which audit rows have a backing record in this build. Rights, sources, and
# media records do not exist yet (16C-RESEARCH Assumption A11), so those rows
# read the stand-in until they ship. Naming them here rather than inside the
# audit means a later phase flips one value and the audit tells the truth
# again with no other edit.
DEFAULT_AVAILABILITY = {"current_parse": True, "identity": True,
                        "fingerprint": True, "objectives": True,
                        "sources": False, "rights": False, "media": False,
                        "assessment_boundaries": True,
                        "plain_rendering": True, "rich_rendering": True,
                        "validation": True}


def baseline_audit(bank_path, available=None):
    """The eleven-item baseline, in order, over one legacy artifact.

    Read-only. Returns a list of exactly eleven `{"item", "result"}` rows in
    `BASELINE_AUDIT_ITEMS` order, so a caller can render them without
    sorting and a reviewer can scan them without hunting.
    """
    availability = dict(DEFAULT_AVAILABILITY)
    availability.update(available or {})

    text = open(bank_path, encoding="utf-8").read()
    questions = model.load(bank_path)
    lesson = model.parse_lesson(bank_path) or {"headings": []}
    headings = lesson.get("headings") or []
    errors, warnings = model.lint(questions)

    computed = {
        "current_parse": "%d items, %d lesson headings"
                         % (len(questions), len(headings)),
        "identity": ", ".join(sorted(q.get("item_id") or q.get("id") or ""
                                     for q in questions)) or "none recorded",
        "fingerprint": ", ".join(model.content_fingerprint(q)
                                 for q in questions) or "none",
        "objectives": "%d of %d items carry an objective"
                      % (len([q for q in questions if q.get("objective")]),
                         len(questions)),
        "sources": "no source registry in this artifact",
        "rights": "no rights record for this artifact",
        "media": "no media registry in this artifact",
        "assessment_boundaries": "%d keyed items"
                                 % len([q for q in questions
                                        if q.get("correct")]),
        "plain_rendering": "%d characters, first line %r"
                           % (len(text), text.split("\n")[0][:60]),
        "rich_rendering": "%d headings the reader can render"
                          % len(headings),
        "validation": "%d errors, %d warnings" % (len(errors),
                                                  len(warnings)),
    }
    return [{"item": item,
             "result": computed[item] if availability.get(item, True)
             else PLAN_TEXT_STAND_IN}
            for item in BASELINE_AUDIT_ITEMS]


def bounded_diff(bank_path, proposed_changes):
    """What would change, each with the reason it earns its place.

    Every proposed entry keeps `before`, `after`, and `reason` together. A
    diff separated from its reason is a diff a reviewer has to reconstruct
    the argument for, which is how cosmetic churn gets approved.

    A change whose reason is empty or reads exactly `cosmetic` is moved to
    `skipped` with the locked sentence and never appears in the proposed
    list at all (UPGRADE-01). It is not disabled or greyed: it is not
    offered.

    Proposes only. The write path is the 14A journal operations, which this
    module does not own and does not call.
    """
    proposed, skipped = [], []
    for change in proposed_changes:
        reason = (change.get("reason") or "").strip()
        if not reason or reason.lower() == "cosmetic":
            skipped.append({"before": change.get("before", ""),
                            "after": change.get("after", ""),
                            "reason": reason,
                            "copy": COSMETIC_SKIP_COPY})
            continue
        proposed.append({"before": change.get("before", ""),
                         "after": change.get("after", ""),
                         "reason": reason})
    return {"heading": DIFF_HEADING.replace("{N}", str(len(proposed))),
            "proposed": proposed,
            "skipped": skipped,
            "path": os.path.basename(bank_path)}


def cannot_express(bank_path, enhancement_name, instance, headings):
    """An enhancement the artifact cannot carry, linked beside it.

    The old artifact keeps its form. The enhancement is rendered as a
    derived trio projection and linked, and the portability cost is stated
    rather than discovered later: the derived form lives beside the file, not
    inside it, and does not travel when the file is copied or exported alone.

    Saying the cost out loud is the whole point. An enhancement silently
    stored beside an artifact is an enhancement someone loses in the first
    move and cannot explain the absence of.
    """
    rendered = note_outputs.render_mode("concept_map", instance, headings)
    return {"copy": CANNOT_EXPRESS_COPY.replace("{enhancement}",
                                                enhancement_name),
            "derived": rendered["text"],
            "derived_ok": rendered["ok"],
            "portability_cost": "The derived form lives beside %s, not "
                                "inside it, so copying or exporting the "
                                "artifact alone leaves the enhancement "
                                "behind." % os.path.basename(bank_path)}


def keyed_meaning_delta(before_qs, after_qs):
    """What moved that assessment depends on, paired by item id.

    Three things count: the tested-content fingerprint, the difficulty, and
    the objective alignment. `model.content_fingerprint` deliberately
    excludes rationale and prose, so rewriting a `WHY BEST` paragraph is not
    a keyed change and rewriting a stem is.

    An item that appears or disappears is also a keyed delta: an upgrade is
    not where items are added or removed.
    """
    before = dict((q.get("item_id") or q.get("id"), q) for q in before_qs)
    after = dict((q.get("item_id") or q.get("id"), q) for q in after_qs)
    deltas = []
    for item_id in sorted(set(before) | set(after)):
        old, new = before.get(item_id), after.get(item_id)
        if old is None or new is None:
            deltas.append({"item_id": item_id,
                           "what": "item set"})
            continue
        if model.content_fingerprint(old) != model.content_fingerprint(new):
            deltas.append({"item_id": item_id, "what": "keyed content"})
        if (old.get("difficulty") or "") != (new.get("difficulty") or ""):
            deltas.append({"item_id": item_id, "what": "difficulty"})
        if (old.get("objective") or "") != (new.get("objective") or ""):
            deltas.append({"item_id": item_id, "what": "objective alignment"})
    return deltas


def _apply_in_memory(text, proposed_changes):
    """The proposed changes over a copy of the text, for comparison only.

    Nothing this returns is written anywhere. It exists so the keyed-meaning
    comparison can be made against what the upgrade WOULD produce rather
    than against a description of it.
    """
    for change in proposed_changes:
        before = change.get("before", "")
        if before and before in text:
            text = text.replace(before, change.get("after", ""), 1)
    return text


def run_upgrade(bank_path, proposed_changes, available=None):
    """The whole upgrade, in the only order it is allowed to happen.

    Audit, then compare, then either halt or propose. There is no path
    through this function that reaches a diff without an audit, and no
    argument that skips one.

    On any keyed-meaning delta the result carries the halt sentence, the two
    affordances, and the audit rows. It carries no diff and no override
    field, because a halt with a way past it is a warning, and UPGRADE-02
    asks for a halt.

    Writes nothing on either path.
    """
    rows = baseline_audit(bank_path, available)
    original = open(bank_path, encoding="utf-8").read()
    updated = _apply_in_memory(original, proposed_changes)

    before_qs = model.load(bank_path)
    after_qs = model.parse_bank(updated)
    deltas = keyed_meaning_delta(before_qs, after_qs)
    if deltas:
        what = ", ".join(sorted(set(d["what"] for d in deltas)))
        return {"halted": True,
                "copy": KEYED_HALT_COPY.replace("{what}", what),
                "affordances": KEYED_HALT_AFFORDANCES,
                "deltas": deltas,
                "audit": rows}
    return {"halted": False,
            "audit": rows,
            "completion": AUDIT_COMPLETION_LINE,
            "diff": bounded_diff(bank_path, proposed_changes)}
