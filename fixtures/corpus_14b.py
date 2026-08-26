"""The synthetic course corpus Phase 14B's graph kernel is proven against.

`build_three_domains(dest)` builds course roots under `dest` and returns a
dict describing what it built. Plan 14B-01 needs only the first domain; plan
14B-02 widens this to three so the freeze gate's three-domain tracer has a
corpus. `build_stub_course(dest)` writes a Phase 13.9 shaped `course.md` so
the non-destructive migration path has a real stub to read.

Every file's content is fictional and generated from a fixed seed, so a
rebuild is byte-identical and this corpus names no real course, book, learner,
or bank (project content rule). It is built into temp directories at test
time, so `python itembank.py guard .` never sees it.

`teardown(dest)` removes a built corpus.
"""
import os
import shutil

# Fictional. Named so it reads as a course without resembling any real one.
DOMAINS = (
    {
        "slug": "meridian-field-response",
        "title": "Meridian Field Response",
        "container": "Scene Size Up",
        "objectives": (
            "Identify scene hazards on arrival",
            "Choose a body substance isolation level",
        ),
    },
    {
        "slug": "lattice-quantitative-methods",
        "title": "Lattice Quantitative Methods",
        "container": "Rates of Change",
        "objectives": (
            "Read a rate of change from a table",
            "Relate a rate of change to its graph",
        ),
    },
    {
        "slug": "harbour-computing-foundations",
        "title": "Harbour Computing Foundations",
        "container": "Values and Names",
        "objectives": (
            "Predict the value a name is bound to",
            "Trace a rebinding through a short program",
        ),
    },
)

STUB_HEADER = (
    "# Course manifest (DRAFT STUB, 2026-08-14)",
    "",
    "This file is a hand-authored draft manifest for one walking-skeleton",
    "course. It records what was discovered, what was bound, and what was",
    "decided, in the smallest readable form. Phase 14B owns the durable",
    "course schema and supersedes this format.",
)

STUB_SOURCES = (
    ("s1", "sources/field-response-unit-1.md", "markdown", "18402",
     "0f1e2d3c4b5a6978"),
    ("s2", "sources/field-response-figures.md", "markdown", "4110",
     "1a2b3c4d5e6f7081"),
)

STUB_OBJECTIVES = (
    ("o1", "Identify scene hazards on arrival",
     "field-response-unit-1.md section 1.2", "lesson plus practice",
     "the source explains it but never drills it"),
    ("o2", "Choose a body substance isolation level",
     "field-response-unit-1.md section 1.4", "direct source reading",
     "the source is already clear and worked"),
    ("o3", "Sequence the first ninety seconds on scene",
     "field-response-unit-1.md section 2.1", "lesson plus practice",
     "the ordering is the whole difficulty"),
)


def _table(columns, rows):
    out = ["| " + " | ".join(columns) + " |",
           "|" + "|".join(["---"] * len(columns)) + "|"]
    for row in rows:
        out.append("| " + " | ".join(row) + " |")
    return out


def build_stub_course(dest):
    """Write a Phase 13.9 shaped `course.md` into `dest` and return its path.

    This is the file `course.migrate_stub` reads and, under D-14B-1, never
    writes. The test asserts its bytes are identical before and after the
    migration, which is the whole point of having a real one here.
    """
    os.makedirs(dest, exist_ok=True)
    lines = list(STUB_HEADER)
    lines.append("")
    lines.append("## Sources")
    lines.append("")
    lines.extend(_table(("id", "path", "format", "size", "sha256"),
                        STUB_SOURCES))
    lines.append("")
    lines.append("## Objectives")
    lines.append("")
    lines.extend(_table(("id", "objective", "citation", "treatment", "reason"),
                        STUB_OBJECTIVES))
    lines.append("")
    lines.append("## Log")
    lines.append("")
    lines.append("- 2026-08-14 drafted by hand from the unit 1 reading.")
    path = os.path.join(dest, "course.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


def build_three_domains(dest):
    """Build the corpus's course roots under `dest`.

    Plan 14B-01 builds only the first domain, which is all the thin slice
    needs; plan 14B-02 widens this to all three for the three-domain tracer.
    The full `DOMAINS` tuple is already declared above so widening it is a
    loop bound change and not a second fixture.
    """
    import course
    import graph

    built = []
    for domain in DOMAINS[:1]:
        root = os.path.join(dest, domain["slug"])
        os.makedirs(root, exist_ok=True)
        course.create_course(root, domain["title"], "agent", "corpus-14b")
        read = course.read_course(root)
        doc = read["doc"]
        container = graph.add_container(doc, "module", domain["container"])
        objective_ids = []
        for statement in domain["objectives"]:
            objective_ids.append(
                graph.add_objective(doc, statement,
                                    container=container["id"])["id"])
        graph.add_edge(doc, objective_ids[0], "prerequisite-of",
                       objective_ids[1],
                       rationale="hazards are read before isolation is chosen")
        course.write_course(root, doc, read["fingerprint"], "agent",
                            "corpus-14b")
        built.append({
            "slug": domain["slug"], "root": root, "title": domain["title"],
            "container": container["id"], "objectives": objective_ids,
            "edges": 1,
        })
    return {"dest": dest, "domains": built, "built": len(built),
            "declared": len(DOMAINS)}


def teardown(dest):
    shutil.rmtree(dest, ignore_errors=True)
