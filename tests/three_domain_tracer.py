#!/usr/bin/env python3
"""The Phase 14B freeze gate: one scripted run proving, on a single synthetic
three-domain corpus, that the course graph reads as plain Markdown a human can
edit, that an edge type this build does not recognize degrades to an advisory
recommendation and never blocks a learner, that splitting and renaming an
objective moves identity without touching one recorded evidence event, and
that a course exported and restored on a clean offline destination validates
against its manifest with every loss named. It refuses to run against a red
suite, it records its measurements as measurements rather than as budgets, and
it prints a named SKIP line for every platform fallback instead of passing
silently.

Standard library only, runnable as `python3 tests/three_domain_tracer.py`.
It adds no capability: plans 14B-01 through 14B-05 built what this proves.
"""
import difflib
import os
import platform
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, TESTS_DIR)
import course                                                 # noqa: E402
import course_package                                         # noqa: E402
import evidence                                               # noqa: E402
import graph                                                  # noqa: E402
import identity                                               # noqa: E402
import fixtures.corpus_14b as corpus_14b                       # noqa: E402

SHIPPED_SUITES = (
    "tests/graph_roundtrip.py",
    "tests/course_package_roundtrip.py",
    "tests/scoring_roundtrip.py",
    "tests/evidence_roundtrip.py",
    "tests/lesson_roundtrip.py",
)

SKIPS = []


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def skip(name, reason):
    line = "SKIP: %s (%s)" % (name, reason)
    SKIPS.append(line)
    print(line)


def eq(found, expected, label):
    if found != expected:
        fail("%s: expected %r, found %r" % (label, expected, found))


# ---------------------------------------------------------------------------


def shipped_suite_check():
    """The precondition. A tracer that runs against a red suite proves
    nothing, so this is the first thing `main` calls and a single non-zero
    exit stops the run by name."""
    results = {}
    for rel in SHIPPED_SUITES:
        proc = subprocess.run([sys.executable, rel], cwd=ROOT,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        results[rel] = proc.returncode
        if proc.returncode != 0:
            print("PRECONDITION FAILED: %s is red; the tracer does not run "
                  "against a red suite" % rel)
            sys.exit(1)
    return results


# ---------------------------------------------------------------------------
# GRAPH-01.


def scenario_three_domain_outline(built):
    """GRAPH-01's Fixture sentence, executed: three domains whose containers
    are labelled differently all project to plain readable Markdown, and
    structural order mints no prerequisite edge."""
    labels = set()
    deliberate_prerequisites = 0
    for domain in built["domains"]:
        read = course.read_course(domain["root"])
        doc = read["doc"]
        for container in doc["structure"]:
            labels.add(container["label"])

        outline = graph.outline_projection(doc)
        again = graph.outline_projection(doc)
        if outline != again:
            fail("scenario_three_domain_outline: two projections of one "
                 "unchanged document differed")
        for line in outline.split("\n"):
            if not line.strip():
                continue
            head = line[0]
            if head not in "#-" and not head.isalpha():
                fail("scenario_three_domain_outline: outline line %r does "
                     "not read as plain Markdown" % line)
            if line.lstrip().startswith("{"):
                fail("scenario_three_domain_outline: outline line %r starts "
                     "with a JSON brace" % line)
            for n, ch in enumerate(line):
                if ch == "<" and n + 1 < len(line) and \
                        (line[n + 1].isalpha() or line[n + 1] == "/"):
                    fail("scenario_three_domain_outline: outline line %r "
                         "carries an HTML tag" % line)
            if chr(0x2014) in line:
                fail("scenario_three_domain_outline: outline line %r carries "
                     "an em dash" % line)

        path = os.path.join(domain["root"], "outline_projection.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(outline)
        with open(path, "r", encoding="utf-8") as fh:
            if fh.read() != outline:
                fail("scenario_three_domain_outline: the outline did not "
                     "survive a write and read cycle byte for byte")

        for record in doc["edges"]:
            if record.get("edge_type") == "prerequisite-of":
                deliberate_prerequisites += 1

    for required in ("module", "week", "chapter", "fortnight"):
        if required not in labels:
            fail("scenario_three_domain_outline: the corpus does not carry a "
                 "%s container label" % required)

    expected = sum(d["prerequisite_edges"] for d in built["domains"])
    eq(deliberate_prerequisites, expected,
       "prerequisite edges across the three domains")

    # Structure alone mints nothing. Containers and objectives are added to a
    # fresh document and the edge table stays empty.
    doc = graph.new_course("Structure Mints Nothing", identity.new_object_id())
    parent = graph.add_container(doc, "semester", "Only Semester")
    for n in range(3):
        child = graph.add_container(doc, "fortnight", "Fortnight %d" % (n + 1),
                                    parent=parent["id"])
        for m in range(2):
            graph.add_objective(doc, "Objective %d.%d" % (n + 1, m + 1),
                                container=child["id"])
    eq(doc["edges"], [], "edges minted by structural order alone")
    return "pass"


# ---------------------------------------------------------------------------
# GRAPH-02.


def scenario_edge_vocabulary(built):
    """GRAPH-02's Fixture sentence, executed: one edge of every registered
    type plus one this build has never heard of, which is kept, downgraded to
    an advisory recommendation, and cannot be argued into blocking."""
    doc = graph.new_course("Edge Vocabulary", identity.new_object_id())
    container = graph.add_container(doc, "module", "Only Module")
    objectives = [graph.add_objective(doc, "Vocabulary objective %d" % n,
                                      container=container["id"])["id"]
                  for n in range(1, 7)]
    source_object_id = identity.new_object_id()
    graph.add_source(doc, source_object_id, "A synthetic source")

    graph.add_edge(doc, objectives[0], "prerequisite-of", objectives[1],
                   authority="authored", confidence="high")
    graph.add_edge(doc, objectives[2], "covers-objective", objectives[3],
                   authority="authored")
    graph.add_edge(doc, source_object_id, "source-supports", objectives[4],
                   authority="imported")
    graph.add_edge(doc, objectives[4], "treatment-of", objectives[5],
                   authority="proposed")
    graph.add_edge(doc, objectives[5], "alternate-path", objectives[0],
                   rationale="an unregistered relation, kept and downgraded")
    eq(len(doc["edges"]), 5, "the edge count on the vocabulary document")

    unknown = doc["edges"][-1]
    reading = graph.validate_edge(unknown)
    eq(reading["effective_type"], "recommended-before",
       "the unknown edge type's effective type")
    eq(reading["authority"], "advisory", "the unknown edge type's authority")
    eq(reading["override"], "advisory", "the unknown edge type's override")
    eq(reading["original_type"], "alternate-path",
       "the unknown edge type's original type, kept")
    if unknown not in doc["edges"]:
        fail("scenario_edge_vocabulary: the unknown edge was dropped rather "
             "than downgraded")

    warnings = graph.validate_order(doc)
    for warning in warnings:
        if "alternate-path" in warning:
            fail("scenario_edge_vocabulary: an unregistered relation produced "
                 "an order warning")

    text = graph.serialize_course(doc)
    # An unknown type argued into a hard gate by hand-editing the file. The
    # effective reading has to stay advisory: a relation this build cannot
    # read is not allowed to block a learner whatever the cell says.
    lines = text.split("\n")
    forced = 0
    for index, line in enumerate(lines):
        if line.startswith("|") and "alternate-path" in line:
            cells = graph.split_row(line)
            cells[-1] = "hard-gate"
            lines[index] = "| " + " | ".join(cells) + " |"
            forced += 1
    eq(forced, 1, "the number of alternate-path rows hand edited")
    forced_doc = graph.parse_course("\n".join(lines))
    forced_edge = [r for r in forced_doc["edges"]
                   if r.get("edge_type") == "alternate-path"][0]
    eq(forced_edge.get("override"), "hard-gate",
       "the hand written override cell is preserved verbatim")
    eq(graph.validate_edge(forced_edge)["override"], "advisory",
       "the effective override of a hand written hard gate on an unknown type")
    eq(graph.validate_edge(forced_edge)["effective_type"],
       "recommended-before", "the forced row's effective type")

    round_tripped = graph.parse_course(graph.serialize_course(
        graph.parse_course(text)))
    eq([r["edge_type"] for r in round_tripped["edges"]],
       [r["edge_type"] for r in doc["edges"]],
       "the five edge type strings after a serialize and parse round trip")
    return "pass"


# ---------------------------------------------------------------------------
# GRAPH-04.


def scenario_migration(built):
    """GRAPH-04's Fixture sentence, executed: a split and a rename each
    produce one reviewed proposal, and not one recorded evidence event moves,
    changes, or is reinterpreted."""
    domain = [d for d in built["domains"]
              if d["slug"] == "lantern-computing"][0]
    root = domain["root"]
    log = evidence.log_path(root)
    before = list(evidence.events(log))
    if not before:
        fail("scenario_migration: the lantern-computing domain carries no "
             "seeded evidence event, so this scenario would prove nothing")
    seeded_objective = domain["objectives"][0]
    before_raw = [dict(ev) for ev in before]

    read = course.read_course(root)
    doc = read["doc"]
    split_from = domain["objectives"][1]
    rename_from = domain["objectives"][2]

    records, split_proposal = graph.split_objective(
        doc, split_from,
        ["Predict a binding before the rebinding runs",
         "Predict a binding after the rebinding runs"],
        "the single statement asked for two separate judgements", "tracer")
    renamed, rename_proposal = graph.rename_objective(
        doc, rename_from, "State the condition on which a loop stops",
        "the original wording read as a question about starting", "tracer")
    course.write_course(root, doc, read["fingerprint"], "agent", "tracer",
                        operation="migrate")

    after_read = course.read_course(root)
    after_doc = after_read["doc"]
    proposals = after_doc["migrations"]
    eq(len(proposals), 2, "one reviewed migration proposal per operation")
    eq(sorted(p["kind"] for p in proposals), ["rename", "split"],
       "the two recorded migration kinds")
    for proposal in proposals:
        eq(proposal["state"], "proposed", "the recorded migration state")
        if not str(proposal.get("rationale", "")).strip():
            fail("scenario_migration: a recorded proposal carries no "
                 "rationale a reviewer could evaluate")

    after = list(evidence.events(log))
    eq(len(after), len(before), "the evidence event count across a migration")
    eq([dict(ev) for ev in after], before_raw,
       "every recorded evidence event, byte for byte, across a migration")
    for ev in after:
        eq(ev.get("objective"), seeded_objective,
           "the objective identity the seeded event still names")

    new_ids = [r["id"] for r in records] + [renamed["id"]]
    for new_id in new_ids:
        count = len([ev for ev in after if ev.get("objective") == new_id])
        eq(count, 0, "events recorded against a freshly minted identity")
        eq(graph.objective_evidence_state(after_doc, new_id, count), "unknown",
           "the evidence state of an unmigrated new identity")
    eq(graph.objective_evidence_state(after_doc, seeded_objective,
                                      len(before)), "present",
       "the evidence state of the original identity")

    # Nothing in this phase settles a proposal, and reaching for a way to do
    # it finds a named refusal rather than an absent function.
    try:
        graph.set_migration_state(after_doc, proposals[0]["migration_id"],
                                  "accepted")
    except graph.GraphError as err:
        eq(err.code, "graph.migration_state_not_settable",
           "the refusal code for settling a migration state")
    else:
        fail("scenario_migration: a migration state was settled in a phase "
             "that implements no acceptance path")
    return "pass"


# ---------------------------------------------------------------------------
# PORT-03.


def scenario_clean_restore(tmp, built):
    """PORT-03's Fixture sentence, executed: a course exported and restored on
    a clean offline destination validates against its manifest and every loss
    is named."""
    domain = built["domains"][0]
    root = domain["root"]

    corpus_14b.packaged_source(root, "carried-source")
    corpus_14b.linked_source(root, "kept-where-it-lives")
    corpus_14b.unreachable_root_case(root)
    # The domain's own source is left at its default rights, which are all
    # unknown, so the rights-restricted row is a real restrictive default and
    # not a denial written to make the assertion pass.

    pkg = os.path.join(tmp, "freeze_gate_package")
    manifest = course_package.export_package(root, root, pkg)
    eq(sorted(manifest.keys()), sorted(course_package.MANIFEST_KEYS +
                                       course_package.MANIFEST_OPTIONAL_KEYS),
       "the manifest key set")
    eq(manifest["state"], "applied", "the finished manifest state")

    sidecar_raw = open(course.sidecar_path(root), "rb").read()
    verified = course_package.verify_manifest(pkg)
    eq(verified["complete"], True, "an untouched package verifies complete")
    eq(verified["entries_verified"], len(manifest["entries"]),
       "every manifest entry verified by recomputation")

    clean = corpus_14b.clean_machine_dest(tmp)
    dest = clean["dest"]
    if os.listdir(dest):
        fail("scenario_clean_restore: the clean destination must start empty")
    saved = {k: os.environ.get(k) for k in clean["env"]}
    try:
        for key, value in clean["env"].items():
            os.environ[key] = value
        restored = course_package.restore_package(pkg, dest, "human", "weibao")
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    eq(restored["complete"], True, "the restore reports itself complete")
    eq(restored["entries_verified"], len(manifest["entries"]),
       "every entry verified on restore")
    if "losses" not in restored or "restore_losses" not in restored:
        fail("scenario_clean_restore: a restore must return both the export "
             "time loss list and its own")
    restored_sidecar = os.path.join(dest, course.COURSE_SIDECAR_FILENAME)
    eq(open(restored_sidecar, "rb").read(), sidecar_raw,
       "the restored sidecar bytes")

    found = {}
    for row in restored["losses"]:
        found.setdefault(row["category"], []).append(row)
    for category in ("external-link", "rights-restricted", "machine-local",
                     "unreachable-source"):
        rows = found.get(category)
        if not rows:
            fail("scenario_clean_restore: no %s row appears in the loss "
                 "report, so a loss went unreported" % category)
        for row in rows:
            if not str(row.get("reason", "")).strip():
                fail("scenario_clean_restore: the %s loss row carries no "
                     "reason" % category)
        if category not in course_package.LOSS_CATEGORIES:
            fail("scenario_clean_restore: %s is not a named loss category"
                 % category)

    # The freeze gate covers the archive refusal directly rather than only
    # through the roundtrip suite: a package can cross a machine boundary.
    archive = corpus_14b.build_traversing_archive(
        os.path.join(tmp, "traversing.zip"))
    extract_dest = os.path.join(tmp, "traversing_dest")
    try:
        course_package.extract_archive(archive, extract_dest)
    except course_package.PackageError as err:
        eq(err.code, "package.path_escape",
           "the refusal code for a traversing archive entry")
    else:
        fail("scenario_clean_restore: a traversing archive entry was not "
             "refused")
    if os.path.exists(os.path.join(tmp, "escape.md")):
        fail("scenario_clean_restore: a traversing archive entry escaped its "
             "root")

    if built["platform"]["archive_symlink_entry"]:
        symlink_zip = corpus_14b.build_symlink_archive(
            os.path.join(tmp, "symlink.zip"))
        try:
            course_package.extract_archive(
                symlink_zip, os.path.join(tmp, "symlink_dest"))
        except course_package.PackageError as err:
            eq(err.code, "package.symlink_payload",
               "the refusal code for a symbolic link archive entry")
        else:
            fail("scenario_clean_restore: a symbolic link archive entry was "
                 "not refused")
    else:
        skip("archive symlink entry refusal",
             "this platform cannot express a symbolic link zip entry")
    return "pass"


# ---------------------------------------------------------------------------
# The machine half of the authorability leg.


def scenario_authorability_roundtrip(tmp, built):
    """The machine half of the authorability review: a human reordering two
    containers by editing one cell produces a one line diff, the reordering
    survives the projection, and no line is too long to read in a plain
    editor. The human half is Task 2's review and is never self certified
    here."""
    domain = built["domains"][0]
    read = course.read_course(domain["root"])
    original = read["text"]

    containers = read["doc"]["structure"]
    if len(containers) < 2:
        fail("scenario_authorability_roundtrip: the domain has fewer than two "
             "containers, so there is nothing to reorder")
    second = containers[1]

    lines = original.split("\n")
    edited, hits = [], 0
    for line in lines:
        if line.startswith("|") and second["id"] in line and \
                second["title"] in line:
            cells = graph.split_row(line)
            cells[3] = "0"
            edited.append("| " + " | ".join(cells) + " |")
            hits += 1
            continue
        edited.append(line)
    eq(hits, 1, "the number of structure rows hand edited")
    edited_text = "\n".join(edited)

    final = graph.serialize_course(graph.parse_course(edited_text))
    changed = [ln for ln in difflib.unified_diff(
        original.split("\n"), final.split("\n"), lineterm="", n=0)
        if (ln.startswith("+") or ln.startswith("-")) and
        not ln.startswith("+++") and not ln.startswith("---")]
    eq(len(changed), 2,
       "the diff of a one cell hand edit, counted as one removed and one "
       "added line")

    before_titles = [ln for ln in graph.outline_projection(
        read["doc"]).split("\n") if ln.startswith("## ")]
    after_titles = [ln for ln in graph.outline_projection(
        graph.parse_course(final)).split("\n") if ln.startswith("## ")]
    if before_titles == after_titles:
        fail("scenario_authorability_roundtrip: the hand edit did not reach "
             "the projection")
    if second["title"] not in after_titles[0]:
        fail("scenario_authorability_roundtrip: the reordered container is "
             "not first in the re-projected outline")

    longest = max(len(ln) for ln in final.split("\n"))
    if longest > 200:
        fail("scenario_authorability_roundtrip: the sidecar carries a line of "
             "%d characters, which does not read in a plain editor" % longest)

    # No path is printed and no file is left behind: two runs of this tracer
    # must produce identical output apart from the budget lines, and a temp
    # directory name is different every time. Task 2 of plan 14B-06 generates
    # the human reviewer's copy separately.
    print("authorability one cell hand edit: 1 line changed, reordering "
          "reached the projection, longest sidecar line %d characters"
          % longest)
    return "pass"


# ---------------------------------------------------------------------------


def measure_budgets():
    """Recorded, never promised. Every figure below is one measurement on one
    machine, and no later phase may assert against it. This follows
    D-12.6-10's measured-not-promised posture and 14B-RESEARCH.md open
    question 3, which recommends no performance budget for this gate."""
    figures = []
    tmp = tempfile.mkdtemp(prefix="three_domain_budget_")
    try:
        start = time.time()
        built = corpus_14b.build_all(tmp)
        figures.append(("build_all", time.time() - start))

        start = time.time()
        for domain in built["domains"]:
            graph.outline_projection(course.read_course(domain["root"])["doc"])
        figures.append(("outline_projection_three_domains",
                        time.time() - start))

        root = built["domains"][0]["root"]
        corpus_14b.packaged_source(root, "budget-source")
        pkg = os.path.join(tmp, "budget_package")
        start = time.time()
        course_package.export_package(root, root, pkg)
        figures.append(("export_package", time.time() - start))

        dest = os.path.join(tmp, "budget_restore")
        os.makedirs(dest, exist_ok=True)
        start = time.time()
        course_package.restore_package(pkg, dest, "human", "weibao")
        figures.append(("restore_package", time.time() - start))
    finally:
        corpus_14b.teardown(tmp)

    lines = []
    for name, seconds in figures:
        line = ("budget %s: %.3f s (measured on this machine, recorded not "
                "promised)" % (name, seconds))
        print(line)
        lines.append(line)
    return lines


# ---------------------------------------------------------------------------


def main():
    shipped_suite_check()

    results = []
    tmp = tempfile.mkdtemp(prefix="three_domain_tracer_")
    try:
        built = corpus_14b.build_all(tmp)
        if built["built"] != built["declared"]:
            fail("main: the corpus built %d of %d declared domains"
                 % (built["built"], built["declared"]))
        if not built["platform"]["symlink"]:
            skip("filesystem symlink creation",
                 "this platform refused to create a symbolic link")
        results.append(("three_domain_outline",
                        scenario_three_domain_outline(built)))
        results.append(("edge_vocabulary", scenario_edge_vocabulary(built)))
        results.append(("migration", scenario_migration(built)))
        results.append(("clean_restore", scenario_clean_restore(tmp, built)))
        results.append(("authorability_roundtrip",
                        scenario_authorability_roundtrip(tmp, built)))
    finally:
        corpus_14b.teardown(tmp)

    for name, status in results:
        print("scenario %s: %s" % (name, status))

    measure_budgets()
    print("platform: %s %s" % (platform.system(), platform.machine()))

    passed = sum(1 for _, status in results if status == "pass")
    print("TRACER: %d passed, %d skipped, 0 failed" % (passed, len(SKIPS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
