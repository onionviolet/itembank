#!/usr/bin/env python3
"""The 17A component primitive fixture (plan 17A-03, VISUAL-01, A11Y-01).

One suite over the whole 16B/16C component inventory 17A-UI-SPEC's Component
Styling Assignments table names, crossed with the seven state rows its UI
Considerations table requires: zero, one, many, error, loading, partial, and
overflow.

Two things this fixture deliberately does NOT do. It does not re-decide any
16B or 16C semantics: every count, order, and control string asserted below is
quoted from 17A-UI-SPEC, and a disagreement between this file and that
document is this file's defect. And it does not measure layout: contrast,
zoom, reflow, and real focus rendering need a layout-capable harness plus a
human pass (D-09, A11Y-01), and an agent never self-certifies accessibility.
What is checkable here is structure and bytes, so that is what is checked.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from surfaces import presentation as P  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def ok(msg):
    print("ok: " + msg)


TAG_RE = re.compile(r"<[^>]+>")
HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgb|hsl)a?\s*\(")

# The inventory, by name, so a component that is deleted or renamed fails here
# rather than quietly leaving a row of the spec unbuilt.
INVENTORY = ("course_shelf", "activity_view", "settings_panel",
             "first_launch_walkthrough", "status_notice",
             "note_capture_panel", "notes_panel_evidence", "strategy_picker",
             "progress_comprehension_display", "note_output_trio",
             "evidence_drawer", "diff_review", "loading_line", "anchor_chip",
             "chip_row", "fill_state", "wrap_path")

LOADING = {"kind": "loading", "of": "notes"}
ERROR = {"kind": "error", "status": "That folder is not readable right now."}


def text_of(markup):
    """The visible text a plain reader gets with every stylesheet removed."""
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", markup)).strip()


def courses(n, locked=False):
    return [{"name": "Course %d" % i, "meta": "Objective %d" % i,
             "locked": locked, "unlock": "Finish the intake first.",
             "chips": [{"label": "Due today", "kind": "warn"}],
             "action": {"label": "Resume", "href": "/course/%d" % i}}
            for i in range(n)]


def jobs(n, status="Running"):
    return [{"name": "Job %d" % i, "status": status,
             "chips": [{"label": "Completed", "kind": "ok"}]}
            for i in range(n)]


def notes(n):
    return [{"text": "Note %d wording" % i,
             "chips": [{"label": "Anchored", "kind": "ok"}]}
            for i in range(n)]


def diffs(n):
    return [{"label": "Change %d" % i, "finding": "Adds a citation.",
             "body": "- old\n+ new",
             "action": {"label": "Accept"},
             "actions": [{"label": "Reject"}]} for i in range(n)]


def objectives(n):
    return [{"label": "Objective %d" % i, "filled": i % 6,
             "legend": "Self-adjustable standing"} for i in range(n)]


def dimensions(n=7):
    return [{"label": "Dimension %d" % i, "text": "Not enough evidence yet."}
            for i in range(n)]


# Every list primitive, with a factory that takes a row count, so the
# zero/one/many/error/loading sweep runs over all of them uniformly instead of
# once per component by hand.
LIST_CASES = (
    ("course_shelf", lambda n, st: P.course_shelf(
        courses(n), empty="No courses yet.", state=st)),
    ("activity_view", lambda n, st: P.activity_view(
        needs_input=jobs(n), empty="No activity yet.", state=st)),
    ("settings_panel", lambda n, st: P.settings_panel(
        [{"label": "Approved roots",
          "rows": [{"label": "Root %d" % i, "path": "/Users/w/course/%d" % i}
                   for i in range(n)]}] if n else [],
        empty="No approved roots yet.", state=st)),
    ("notes_panel_evidence", lambda n, st: P.notes_panel_evidence(
        [{"objective": "Objective A", "notes": notes(n)}] if n else [],
        empty="No notes yet for this course.", state=st)),
    ("strategy_picker", lambda n, st: P.strategy_picker(
        [{"name": "Strategy %d" % i, "purpose": "What it is for.",
          "chips": [{"label": "Locked", "kind": "unknown"}]}
         for i in range(n)],
        empty="No strategies available.", state=st)),
    ("progress_comprehension_display", lambda n, st:
     P.progress_comprehension_display(
         dimensions() if n else (), objectives(n),
         empty="Not enough evidence yet.", state=st)),
    ("note_output_trio", lambda n, st: P.note_output_trio(
        sections=[{"label": "Section %d" % i, "body": "Body."}
                  for i in range(n)],
        adjacency=["A relates to B"] * n,
        empty="No note yet.", state=st)),
    ("evidence_drawer", lambda n, st: P.evidence_drawer(
        "Why this item?", ["Entry %d" % i for i in range(n)],
        empty="No evidence recorded yet.", state=st)),
    ("diff_review", lambda n, st: P.diff_review(
        diffs(n), empty="No proposed changes.", state=st)),
)


def check_inventory_is_complete():
    """Every component the spec's table names exists as one callable."""
    missing = [name for name in INVENTORY if not callable(getattr(P, name,
                                                                  None))]
    if missing:
        fail("17A-UI-SPEC's component table names %s, and this module exposes "
             "no primitive for them" % ", ".join(missing))
    ok("inventory: %d primitives, one per component row" % len(INVENTORY))


def check_zero_state_renders_copy_not_a_control():
    """Contract section 6: a section that would collapse to nothing renders
    its empty copy directly, never a disclosure with nothing behind it."""
    for name, build in LIST_CASES:
        markup = build(0, None)
        if "<details" in markup:
            fail("%s renders a disclosure control at zero rows; an empty "
                 "section shows its copy instead" % name)
        if not text_of(markup):
            fail("%s renders nothing at zero rows, so a learner cannot tell "
                 "an empty list from a broken one" % name)
        for banned in ("Show all", "Show next", "Show earlier"):
            if banned in markup:
                fail("%s offers %r over an empty list" % (name, banned))
    ok("zero: %d primitives render empty copy and no control" % len(LIST_CASES))


def check_one_and_many_render_every_row():
    """One row and many rows differ only in count. No primitive drops a row,
    and none of them summarises a count into an aggregate nobody computed."""
    for name, build in LIST_CASES:
        one, many = build(1, None), build(8, None)
        if text_of(one) == text_of(many):
            fail("%s renders one row and eight rows identically" % name)
        # Eight rows sits under every pagination bound in the layer, so a
        # missing row here is a dropped row rather than a paged one. The
        # bounds themselves are asserted at their exact counts in the
        # overflow check below.
        for n in (1, 8):
            markup = build(n, None)
            for row in range(n):
                # Every factory numbers its rows, and every row's number must
                # survive to the served text somewhere, expanded or not.
                if str(row) not in text_of(markup):
                    fail("%s at %d rows dropped row %d from its text"
                         % (name, n, row))
    ok("one and many: every row survives to text in all %d primitives"
       % len(LIST_CASES))


def check_loading_is_a_stated_line():
    """A slow read shows a stated Ledger-voice line announced once, never a
    wordless spinner and never a bare control."""
    for name, build in LIST_CASES:
        markup = build(6, LOADING)
        if "Loading" not in markup:
            fail("%s under a slow read shows no stated loading line" % name)
        if 'role="status"' not in markup:
            fail("%s announces its slow read through no live region" % name)
        if "spin" in markup.lower():
            fail("%s renders a spinner" % name)
        if "Course 0" in markup or "Note 0" in markup:
            fail("%s renders rows while claiming to still be reading" % name)
    line = P.loading_line("notes")
    if "Loading notes" not in line:
        fail("the loading line does not name what is loading")
    ok("loading: %d primitives show one stated, announced line"
       % len(LIST_CASES))


def check_error_keeps_the_surface_recoverable():
    """A failed read shows the surface's own degraded copy in a live region,
    and never renders group headings over content that failed."""
    for name, build in LIST_CASES:
        markup = build(6, ERROR)
        if ERROR["status"] not in markup:
            fail("%s drops the degraded-state copy on a failed read" % name)
        if 'role="status"' not in markup:
            fail("%s reports a failed read outside any live region" % name)
        if "Objective A" in markup or "Course 0" in markup:
            fail("%s renders rows over a failed read" % name)
    ok("error: %d primitives render degraded copy and no stale rows"
       % len(LIST_CASES))


def check_partial_states_never_invent_a_number():
    """The partial rows of the spec's table: an in-progress job states its
    status and no percent, and a pending mark pairs the pending token with a
    required text label."""
    running = P.activity_view(in_progress=jobs(3, status="Sourcing"))
    if "Sourcing" not in running:
        fail("an in-progress job must state its status in words")
    if "%" in text_of(running):
        fail("an in-progress job invented a percent; no module on disk "
             "produces one")
    pending = P.anchor_chip("Awaiting review", "pending")
    if 'data-state="pending"' not in pending:
        fail("a pending mark must carry the pending state")
    if "Awaiting review" not in text_of(pending):
        fail("a pending mark must carry its required text label")
    partial_fill = P.fill_state(2, "Self-adjustable standing")
    if partial_fill.count("<i") != P.FILL_BLOCKS:
        fail("a partial standing must still render all five blocks")
    if partial_fill.count('class="on"') != 2:
        fail("a partial standing must fill exactly its own count")
    ok("partial: stated status, no percent, pending labelled, 2 of 5 filled")


def check_overflow_bounds_match_the_spec():
    """Every bounded list, at the exact counts 17A-UI-SPEC fixes."""
    shelf = P.course_shelf(courses(40))
    if "<details" in shelf or "Show" in shelf:
        fail("the shelf paginates; Direction-Neutral #1 says it scrolls at "
             "any card count")
    if shelf.count('class="ib-card"') != 40:
        fail("the shelf clipped its list")

    activity = P.activity_view(needs_input=jobs(9), history=jobs(9))
    head, _, tail = activity.partition("<details")
    if P.ACTIVITY_NEEDS_INPUT not in head:
        fail("the actionable group must render before any disclosure")
    if head.count("Job ") < 9:
        fail("the needs-your-input group collapsed; it never collapses at "
             "any count")
    if P.SHOW_EARLIER_ACTIVITY not in tail:
        fail("history past five must sit behind %r"
             % P.SHOW_EARLIER_ACTIVITY)
    if head.count('class="ib-card"') != 9 + P.ACTIVITY_HISTORY_SHOWN:
        fail("history shows its five most recent above the disclosure")

    for count, expect in ((3, False), (5, True)):
        panel = P.notes_panel_evidence([{"objective": "Objective A",
                                         "notes": notes(count)}])
        has = "<details" in panel
        if has != expect:
            fail("a group of %d notes %s a disclosure"
                 % (count, "must not carry" if has else "must carry"))
        if expect and (P.SHOW_ALL_NOTES % count) not in panel:
            fail("the notes disclosure must name the group's real total")
        before = panel.partition("<details")[0]
        if "Objective A" not in before:
            fail("a group heading must stay visible above its disclosure")
        if before.count('class="ib-card"') != min(count, P.NOTES_PER_GROUP):
            fail("a group shows its first three notes, not %d"
                 % before.count('class="ib-card"'))

    progress = P.progress_comprehension_display(dimensions(), objectives(14))
    dims = progress.partition("<details")[0]
    if dims.count("Dimension ") != 7:
        fail("all seven claim dimensions render above any disclosure; an "
             "aggregate never hides its parts")
    if (P.SHOW_ALL_OBJECTIVES % 14) not in progress:
        fail("per-objective standing past ten needs its named control")
    if dims.count("Objective ") != P.OBJECTIVE_FILL_SHOWN:
        fail("ten objectives stay visible, not %d" % dims.count("Objective "))

    for count, expect in ((10, False), (12, True)):
        review = P.diff_review(diffs(count))
        if "<details" in review:
            fail("a diff must never be collapsed; a reviewer reads it "
                 "without an extra click")
        if (P.SHOW_NEXT_DIFFS in review) != expect:
            fail("a list of %d diffs got the pagination control wrong"
                 % count)
        shown = review.count('class="ib-card ib-diff"')
        if shown != min(count, P.DIFF_PAGE_SIZE):
            fail("a diff page shows ten, not %d" % shown)
    ok("overflow: shelf scrolls, activity 5, notes 3, objectives 10, "
       "diffs 10, dimensions never")


def check_no_truncation_anywhere_it_is_not_authorised():
    """One clip is authorised in the whole layer, and it happens in Python."""
    for banned in ("nowrap", "text-overflow", "ellipsis"):
        if banned in P.PRIMITIVE_CSS.lower():
            fail("the primitive stylesheet declares %r; meaningful text wraps"
                 % banned)
    path = "/Users/weiwei/Documents/Dev/itembank/courses/emt/module-01"
    wrapped = P.wrap_path(path)
    if "<wbr>" not in wrapped:
        fail("a long path must offer a break point at each separator")
    if path not in text_of(wrapped).replace(" ", ""):
        fail("a path lost characters; the root is never hidden from a "
             "learner auditing which folders an agent may read")

    long_label = "Cardiogenic shock compensation"
    trio = P.note_output_trio(mode="map", nodes=[long_label],
                              adjacency=["%s relates to preload" % long_label])
    node = trio.partition('class="ib-nodes"')[2].partition("</ul>")[0]
    if long_label in node:
        fail("the decorative node label did not clip")
    if "…" not in node:
        fail("a clipped node label must show that it was clipped")
    if 'aria-hidden="true"' not in trio.partition("<ul")[2][:120]:
        fail("the decorative node list must be hidden from assistive "
             "technology, since the adjacency list is the accessible form")
    after = trio.partition("Related concepts")[2]
    if long_label not in after:
        fail("the accessible adjacency list must never clip")
    ok("truncation: none in CSS, one clipped decorative node, path intact")


def check_states_are_never_colour_alone():
    """Every semantic state carries a required text label, and an unknown
    state name falls back to neutral rather than to a plausible guess."""
    for kind in P.SEMANTIC_KINDS:
        chip = P.anchor_chip("Label for %s" % kind, kind)
        if 'data-state="%s"' % kind not in chip:
            fail("chip %r lost its state name" % kind)
        if "Label for %s" % kind not in text_of(chip):
            fail("chip %r carries no text label" % kind)
    if 'data-state="neutral"' not in P.anchor_chip("Something", "invented"):
        fail("an unrecognised state must fall back to neutral rather than "
             "being painted as a state this layer does not know")
    notice = P.status_notice("The runtime is unreachable.", "bad",
                             label="Offline", urgent=True)
    if 'role="alert"' not in notice:
        fail("an interrupting notice takes role=alert")
    if "<details" in notice:
        fail("a status notice is never collapsed")
    if "Offline" not in text_of(notice):
        fail("a status notice's severity must be readable as text")
    quiet = P.status_notice("Saved.", "ok")
    if 'role="status"' not in quiet or "alert" in quiet:
        fail("an ordinary notice stays a polite status region")
    ok("colour: every state labelled in text, unknown states go neutral")


def check_fill_state_is_discrete_and_never_a_probability():
    for filled in range(0, 6):
        markup = P.fill_state(filled, "Self-adjustable standing")
        if markup.count("<i") != P.FILL_BLOCKS:
            fail("a standing renders five discrete blocks at every value")
        if markup.count('class="on"') != filled:
            fail("filled count must equal the standing")
        if "%" in text_of(markup):
            fail("a standing must never render a probability")
        if "Self-adjustable standing" not in text_of(markup):
            fail("the fixed legend text sits beside the blocks at all times")
        if 'aria-label="%d of %d"' % (filled, P.FILL_BLOCKS) not in markup:
            fail("the blocks are decorative, so the group needs the same "
                 "discrete count as its accessible name")
    if P.fill_state(99, "x").count('class="on"') != P.FILL_BLOCKS:
        fail("a standing past the block count clamps rather than overflowing")
    ok("fill state: 0 through 5 discrete, legend always adjacent, clamped")


def check_disclosures_are_native_and_named():
    """Every disclosure in the layer is a native details/summary whose summary
    names its content. No hand-authored aria-expanded, no bare More."""
    everything = "".join([
        P.activity_view(needs_input=jobs(1), history=jobs(9)),
        P.notes_panel_evidence([{"objective": "A", "notes": notes(5)}]),
        P.progress_comprehension_display(dimensions(), objectives(14)),
        P.evidence_drawer("Why this item?", ["one", "two"]),
    ])
    if everything.count("<details") != everything.count("<summary"):
        fail("a disclosure without a summary is not keyboard operable")
    if "aria-expanded" in everything:
        fail("a native details element carries its own expanded state; a "
             "hand-authored aria-expanded competes with it")
    for summary in re.findall(r"<summary>(.*?)</summary>", everything):
        if summary.strip().lower() in ("more", "details", "show more"):
            fail("summary %r does not name what it contains" % summary)
    if P.REVIEW_EVIDENCE not in everything:
        fail("the evidence drawer must reuse the locked control string")
    ok("disclosure: native details, named summaries, no authored ARIA")


def check_focus_order_and_no_traps():
    """Nothing in the layer reorders the tab sequence, steals focus on load,
    or hides a focusable control from assistive technology."""
    markup = "".join([
        P.course_shelf(courses(2)),
        P.diff_review(diffs(12)),
        P.first_launch_walkthrough({"label": "Start here",
                                    "body": "One short sentence.",
                                    "action": {"label": "Start"},
                                    "actions": [{"label": "Skip"}]}),
        P.note_capture_panel(label="Note", anchor_label="At: paragraph 3",
                             role_line="A note is yours, not course truth.",
                             privacy_line="Stays on this machine.",
                             action={"label": "Save"}),
    ])
    if "autofocus" in markup:
        fail("a primitive steals focus on load")
    for value in re.findall(r'tabindex="(-?\d+)"', markup):
        if int(value) > 0:
            fail("a positive tabindex reorders the page's tab sequence")
    hidden = re.findall(r'aria-hidden="true"[^>]*>(.*?)</', markup)
    for chunk in hidden:
        if "<button" in chunk or "<a " in chunk:
            fail("a focusable control is hidden from assistive technology")
    # One primary action per action row, never two. The "one primary action
    # per screen" half of the accent rule belongs to whatever composes these
    # into a page, and this layer cannot assert it: a shelf of ten courses is
    # ten cards, each with its own resume control.
    for row in re.findall(r'<div class="actions">(.*?)</div>', markup):
        if row.count("data-action-primary") > 1:
            fail("an action row offers two primary actions")
    if "data-action-primary" not in markup:
        fail("a component that names a primary action rendered none")
    if "Skip" not in markup or "data-action-secondary" not in markup:
        fail("a secondary action must render, and never as the primary one")
    ok("focus: no autofocus, no positive tabindex, no hidden controls")


def check_touch_targets_and_capture_growth():
    css = P.PRIMITIVE_CSS
    if "min-height:44px" not in css.replace(" ", ""):
        fail("the capture field must hold the 44px target floor")
    for prop in ("min-height", "min-width"):
        for match in re.finditer(prop + r"\s*:\s*([^;}]+)", css):
            if "--density-" in match.group(1):
                fail("a target sized from a density token shrinks when a "
                     "panel goes compact; the 44px floor is fixed")
    if "max-height" not in css or "overflow-y:auto" not in css.replace(" ", ""):
        fail("the capture field must grow then scroll inside itself, so the "
             "anchored block underneath stays in view")
    panel = P.note_capture_panel(
        label="Note", role_line="Yours, not course truth.",
        privacy_line="Stays on this machine.", value="typed so far")
    if "<details" in panel:
        fail("the role and privacy lines are never collapsed")
    if "typed so far" not in panel:
        fail("a failed or re-rendered save must never discard typed text")
    if '<label for="note-capture"' not in panel:
        fail("the capture field needs a real label element")
    ok("targets: 44px fixed, field grows then scrolls, panel lines visible")


def check_plain_html_stays_understandable():
    """Semantic equivalence: with every stylesheet gone, each component still
    reads as itself. This is the fallback a reader mode, a text browser, and a
    screen reader all get."""
    cases = {
        "course_shelf": (P.course_shelf(courses(2)), ["Course 0", "Resume"]),
        "activity_view": (P.activity_view(needs_input=jobs(1),
                                          history=jobs(7)),
                          [P.ACTIVITY_NEEDS_INPUT, P.ACTIVITY_HISTORY]),
        "settings_panel": (P.settings_panel(
            [{"label": "Approved roots",
              "rows": [{"label": "Course folder", "path": "/a/b"}]}]),
            ["Approved roots", "Course folder"]),
        "walkthrough": (P.first_launch_walkthrough(
            {"label": "Start here", "body": "A whole sentence that wraps.",
             "action": {"label": "Start"}}),
            ["Start here", "A whole sentence that wraps."]),
        "strategy_picker": (P.strategy_picker(
            [{"name": "Interleave", "purpose": "Mix objectives.",
              "chips": [{"label": "Locked", "kind": "unknown"}]}]),
            ["Interleave", "Mix objectives.", "Locked"]),
        "note_output_trio": (P.note_output_trio(
            sections=[{"label": "Cue", "body": "One idea."}],
            adjacency=["Cue relates to Summary"]),
            ["Cue", "One idea.", "Cue relates to Summary"]),
        "evidence_drawer": (P.evidence_drawer("Why this item?", ["Missed it"]),
                            ["Why this item?", P.REVIEW_EVIDENCE, "Missed it"]),
        "diff_review": (P.diff_review(diffs(1)),
                        ["Change 0", "Accept", "Reject"]),
    }
    for name, (markup, wanted) in cases.items():
        plain = text_of(markup)
        for phrase in wanted:
            if phrase not in plain:
                fail("%s loses %r once its stylesheet is gone" % (name, phrase))
    ok("plain html: %d components readable with no CSS at all" % len(cases))


def check_hostile_text_cannot_break_out():
    hostile = '<script>alert(1)</script> & "quoted" \'and\' <b>bold</b>'
    markup = "".join([
        P.course_shelf([{"name": hostile, "meta": hostile,
                         "chips": [{"label": hostile, "kind": "ok"}]}]),
        P.wrap_path(hostile),
        P.status_notice(hostile, "warn", label=hostile),
        P.note_capture_panel(value=hostile),
        P.diff_review([{"label": hostile, "body": hostile}]),
    ])
    if "<script>" in markup:
        fail("a component let authored text open a script element")
    if "alert(1)" not in markup:
        fail("escaped text must still be present, just inert")
    ok("escaping: markup in content stays inert and still readable")


def check_stylesheet_owns_no_palette():
    css = P.PRIMITIVE_CSS
    hits = HEX_RE.findall(css)
    if hits:
        fail("the primitive stylesheet owns a raw palette value: %s" % hits)
    if css.count("var(--accent)") != 1:
        fail("the accent is reserved for focus, the current nav item and one "
             "primary action; the walkthrough border is its single use here")
    for token in ("--space-", "--density-", "--r-", "--font-"):
        if token not in css:
            fail("the primitive stylesheet defines its own %s spacing rather "
                 "than consuming the frozen token" % token)
    if P.PRIMITIVE_CSS not in P.SHARED_CSS:
        fail("the primitive stylesheet is not in the one shared sheet, so a "
             "surface would have to ship a second one")
    ok("tokens: no palette value, accent used once, one shared sheet")


def check_no_em_dash():
    path = os.path.join(ROOT, "surfaces", "presentation.py")
    with open(path, encoding="utf-8") as fh:
        body = fh.read()
    start = body.find("17A-03: the accessible component primitive layer")
    if start < 0:
        fail("the 17A-03 section marker is gone from presentation.py")
    # Spelled as an escape so the detector does not itself carry the
    # character it bans.
    if "\u2014" in body[start:]:
        fail("an em dash entered repository-authored prose")
    ok("prose: no em dash in anything 17A-03 added")


def main():
    check_inventory_is_complete()
    check_zero_state_renders_copy_not_a_control()
    check_one_and_many_render_every_row()
    check_loading_is_a_stated_line()
    check_error_keeps_the_surface_recoverable()
    check_partial_states_never_invent_a_number()
    check_overflow_bounds_match_the_spec()
    check_no_truncation_anywhere_it_is_not_authorised()
    check_states_are_never_colour_alone()
    check_fill_state_is_discrete_and_never_a_probability()
    check_disclosures_are_native_and_named()
    check_focus_order_and_no_traps()
    check_touch_targets_and_capture_growth()
    check_plain_html_stays_understandable()
    check_hostile_text_cannot_break_out()
    check_stylesheet_owns_no_palette()
    check_no_em_dash()
    print("ok: component primitives roundtrip -- %d components across zero, "
          "one, many, error, loading, partial and overflow" % len(INVENTORY))


if __name__ == "__main__":
    main()
