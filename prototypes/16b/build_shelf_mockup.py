#!/usr/bin/env python3
"""Render the 16B-04 course-shelf mockup from real Phase 14B course records.

Development-only. This is a mockup generator, not a surface: it holds no key,
scores nothing, reaches no session state, registers no route, and is not
imported by any shipped module. It sits beside `prototypes/17a/` for the same
reason that directory exists, and it is deletable without touching anything.

Why generate rather than hand-write the HTML. The first draft of this mockup
invented its own course names, container counts, and IDs, which made every
number in it a decoration. This version builds `fixtures/corpus_14b.py`'s three
synthetic domains into a temp directory, reads them back through
`course.read_course`, and renders the cards from what `graph.py` actually
stores. Container labels, objective counts, source counts, edge counts, course
object IDs and the journal's object state are therefore real values produced by
shipped code.

Percentages are shown. Weibao's 2026-08-27 direction overrides plan 16B-04's
prohibition on a percent character, and `USER-VISION.md` records that user
vision outranks a contract. Rather than fabricate a ratio, every percentage
here is computed from a real numerator over a real denominator that `graph.py`
actually holds: objectives carrying an accepted treatment binding, over
objectives. The generator binds those treatments itself through
`course.bind_treatment` after granting the right, so the coverage figure is a
measured property of the records rather than a decoration.

What is still invented, and is labelled as such in the output:

  * the attention state
  * the resume cue
  * the last-activity date

None of the three can be sourced today, and that is the mockup's most useful
finding rather than a shortcut. `course_shelf_state` belongs to plan 16B-04 and
does not exist; nothing in `graph.py` holds a date, which is the open half of
IL-20260826-07; and a resume cue needs evidence the course sidecar deliberately
never touches, since `course.py` imports no `evidence` by design. Every card
below therefore carries a marker on the fields that are illustration.

Regeneration is byte-identical except for the three course object IDs, which
`identity.new_object_id()` mints fresh on every build. Those three lines are the
only expected diff. Anything else moving between two runs means a shipped record
shape changed, which makes this generator a cheap canary on `graph.py` and
`course.py`.

The corpus is fictional and built into a temp directory, so
`python itembank.py guard .` never sees it. Usage:

    python prototypes/16b/build_shelf_mockup.py > prototypes/16b/course-shelf.html
"""
import html
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "fixtures"))

import corpus_14b
import course
import graph


# Illustration only. Plan 16B-04 fixes that ATTENTION_ORDER exists and is a
# total order; it does not fix which state outranks which, so this ordering is
# the mockup's own and is marked as such wherever it shows.
ILLUSTRATIVE_ATTENTION = [
    ("needs your input", "bad"),
    ("needs reconciliation", "bad"),
    ("due", "warn"),
    ("pending review", "pending"),
    ("Showing last valid overview", "unknown"),
    ("up to date", "ok"),
]

# Illustration only. A resume cue must be server-computed from evidence
# (16B-04), and no such computation exists.
ILLUSTRATIVE_CUES = [
    "Choose a treatment for objective 2 of 6",
    "Continue Rates of Change, item 3 of 9",
    "Review 4 drafted items for Values and Names",
]
ILLUSTRATIVE_DATES = ["2026-08-26", "2026-08-24", "2026-08-21"]

# How many objectives in each domain get an accepted treatment binding. Chosen
# so the three cards show different real coverage rather than three identical
# figures. The bindings are genuine: `course.bind_treatment` writes them through
# the compare-and-swap path and refuses without the right, so these numerators
# are measured back out of the sidecar, not asserted here.
BIND_COUNTS = [4, 2, 5]
BIND_KINDS = ("guided-lesson", "practice", "direct-reading",
              "worked-example", "notes-or-terms")

AREAS = ("Overview", "Learn", "Practice", "Test", "Course map",
         "Sources", "Build and review", "Evidence")

# Contractual. Quoted from plan 16B-04's must-have truths.
EMPTY_HEADING = "No courses yet"
EMPTY_BODY = ("Start with the sample course, or bind a source to create your "
              "first course.")


def bind_some_treatments(dom, how_many):
    """Bind real treatments so design coverage is a measured value.

    Grants `read` and `transform` on the domain's source first, because
    `course.bind_treatment` refuses without the right. That refusal is the
    point of the rights gate, so the mockup goes through it rather than around.
    """
    root = dom["root"]
    source = dom["source_object_id"]
    for operation in ("read", "transform"):
        corpus_14b.grant_right(root, source, operation)
    objectives = course.read_course(root)["doc"]["objectives"]
    for n, objective in enumerate(objectives[:how_many]):
        course.bind_treatment(root, objective["id"], source,
                              BIND_KINDS[n % len(BIND_KINDS)],
                              state="accepted", confidence="high",
                              actor_name="shelf mockup")


def read_domains(dest):
    """Build the 14B corpus and return one fact dict per real course."""
    info = corpus_14b.build_three_domains(dest)
    out = []
    for i, dom in enumerate(info["domains"]):
        bind_some_treatments(dom, BIND_COUNTS[i])
        record = course.read_course(dom["root"])
        doc = record["doc"]
        # Measured back out of the sidecar rather than taken from BIND_COUNTS,
        # so a binding that silently failed shows up as a lower number here.
        treated = len(set(
            b.get("objective", "") for b in doc["bindings"]
            if b.get("binding_kind") == "treatment"
            and b.get("state") == "accepted"))
        total = len(doc["objectives"])
        pct = int(round(100.0 * treated / total)) if total else 0
        labels = []
        for container in doc["structure"]:
            label = container.get("label", "")
            if label and label not in labels:
                labels.append(label)
        out.append({
            "title": doc["header"]["title"],
            "object_id": doc["header"]["course_object_id"],
            "slug": dom["slug"],
            "state": record["state"],
            "revision": record["revision"],
            "containers": len(doc["structure"]),
            "container_titles": [c.get("title", "") for c in doc["structure"]],
            "labels": labels,
            "objectives": len(doc["objectives"]),
            "sources": len(doc["sources"]),
            "edges": len(doc["edges"]),
            "treated": treated,
            "pct": pct,
            "attention": ILLUSTRATIVE_ATTENTION[i][0],
            "tone": ILLUSTRATIVE_ATTENTION[i][1],
            "cue": ILLUSTRATIVE_CUES[i],
            "date": ILLUSTRATIVE_DATES[i],
        })
    return out


def esc(text):
    return html.escape(str(text), quote=True)


def card(facts):
    labels = ", ".join(facts["labels"]) or "none"
    areas = "".join('<a href="#">%s</a>' % esc(a) for a in AREAS)
    return """
      <article class="card s-{tone}">
        <div>
          <h3 class="cname">{title}</h3>
          <div class="cid mono">{oid}</div>
        </div>
        <span class="chip c-{tone}"><span class="dot"></span>{attention}<span
          class="mark" title="Illustration. No shipped code computes an attention state.">i</span></span>
        <p class="cue"><span class="lab">Resume<span class="mark"
          title="Illustration. A resume cue must be computed from evidence, which the course sidecar deliberately never touches.">i</span></span>{cue}</p>
        <div class="prog">
          <div class="pline">
            <span class="plab">Objectives with an accepted treatment</span>
            <span class="pval mono">{treated} of {objectives} &middot; {pct}%</span>
          </div>
          <div class="bar"><i style="width:{pct}%"></i></div>
          <div class="pnote">Real numerator and denominator, read from the sidecar's treatment bindings.</div>
        </div>
        <div class="areas">{areas}</div>
        <dl class="facts">
          <div><dt>Objectives</dt><dd class="mono">{objectives}</dd></div>
          <div><dt>Containers</dt><dd class="mono">{containers}</dd></div>
          <div><dt>Edges</dt><dd class="mono">{edges}</dd></div>
          <div><dt>Sources</dt><dd class="mono">{sources}</dd></div>
        </dl>
        <div class="meta">
          <span>Labels: <span class="mono">{labels}</span></span>
          <span>state <span class="mono">{state}</span>, rev <span class="mono">{revision}</span></span>
        </div>
      </article>""".format(
        tone=esc(facts["tone"]), title=esc(facts["title"]),
        oid=esc(facts["object_id"]), attention=esc(facts["attention"]),
        cue=esc(facts["cue"]), areas=areas,
        objectives=facts["objectives"], containers=facts["containers"],
        edges=facts["edges"], sources=facts["sources"],
        labels=esc(labels), state=esc(facts["state"]),
        revision=facts["revision"], treated=facts["treated"],
        pct=facts["pct"])


def degraded_card():
    """A course whose record cannot be read still renders (16B-04)."""
    return """
      <article class="card s-unknown">
        <div>
          <h3 class="cname">Harbour Signals and Navigation</h3>
          <div class="cid mono">unreadable</div>
        </div>
        <span class="chip c-unknown"><span class="dot"></span>Showing last valid overview</span>
        <p class="cue none"><span class="lab">Resume</span>Not started</p>
        <div class="prog">
          <div class="pline"><span class="plab">Objectives with an accepted treatment</span><span class="pval mono">unknown</span></div>
          <div class="pnote">No percentage is shown, because the record could not be read. A percent with no denominator behind it is the one case still worth refusing.</div>
        </div>
        <div class="recover">
          <a class="btn primary" href="#">Open last valid overview</a>
          <a class="btn" href="#">View files</a>
        </div>
        <div class="meta"><span>Record could not be read</span><span
          class="mono">state unavailable</span></div>
      </article>"""


def render(domains, stamp):
    cards = "".join(card(d) for d in domains) + degraded_card()
    rows = "".join(
        '<tr><td class="rank mono">%d</td><td>%s</td>'
        '<td><span class="chip c-%s"><span class="dot"></span>%s</span></td></tr>'
        % (i + 1, esc(name), esc(tone), esc(name))
        for i, (name, tone) in enumerate(ILLUSTRATIVE_ATTENTION))
    real_note = ", ".join(
        "%s (%d objectives, %d containers)" % (d["title"], d["objectives"],
                                               d["containers"])
        for d in domains)
    page = TEMPLATE
    for token, value in (("@@CARDS@@", cards), ("@@ROWS@@", rows),
                         ("@@STAMP@@", esc(stamp)),
                         ("@@EMPTY_HEADING@@", esc(EMPTY_HEADING)),
                         ("@@EMPTY_BODY@@", esc(EMPTY_BODY)),
                         ("@@REAL_NOTE@@", esc(real_note))):
        page = page.replace(token, value)
    return page


TEMPLATE = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "shelf_template.html"), encoding="utf-8").read()


def main():
    dest = tempfile.mkdtemp(prefix="shelf-mockup-")
    try:
        domains = read_domains(dest)
        stamp = ("built from fixtures/corpus_14b.py via course.bind_treatment "
                 "and course.read_course")
        sys.stdout.write(render(domains, stamp))
    finally:
        shutil.rmtree(dest, ignore_errors=True)


if __name__ == "__main__":
    main()
