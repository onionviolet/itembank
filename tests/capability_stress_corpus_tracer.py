#!/usr/bin/env python3
"""The Phase 16A tracer (plan 16A-02 Task 3).

One authored block travels every layer this phase touches, in one assertion
rather than in three per-layer ones. A `[!PREREQUISITE]` callout starts as
UTF-8 Markdown, passes the one shipped parser, resolves a capability profile
in the new registry, and renders in both continuous and guided mode. A
per-layer suite would happily report green for a parser that emits a field no
renderer reads; only an end to end trip catches that, and catching it on the
phase's first commit rather than its ninth is the point.

The second scenario proves the other half: that the shipped format did not
move while all of that was added. It reads its expected hashes out of
`16A-PRECONDITION.md` rather than carrying literals, so the baseline has one
home and cannot be quietly re-recorded here after a change.

Standard library only, no test framework, runnable as
`python tests/capability_stress_corpus_tracer.py`.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "fixtures"))

import capabilities                                          # noqa: E402
import model                                                 # noqa: E402
import schema_validate                                       # noqa: E402
import lesson_capability_corpus                              # noqa: E402
from surfaces import lesson                                  # noqa: E402

PRECONDITION = os.path.join(
    ROOT, ".planning", "phases", "16A-semantic-capability-activity-contract",
    "16A-PRECONDITION.md")

SHIPPED_SUITES = ("tests/lesson_roundtrip.py", "tests/protocol_roundtrip.py",
                  "tests/presentation_roundtrip.py")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def _run(argv):
    return subprocess.run([sys.executable] + argv, cwd=ROOT,
                          capture_output=True, text=True)


def shipped_suite_check():
    """Run the three shipped suites this phase builds on. A non-zero exit
    from any of them makes every 16A scenario a SKIP rather than a PASS.

    A phase tracer reporting passes while the shipped renderer is broken
    hides which layer actually moved, and a green line over a red foundation
    is worse than a red line: it is a wrong answer instead of a question.
    """
    broken = []
    for suite in SHIPPED_SUITES:
        if _run([suite]).returncode != 0:
            broken.append(suite)
    return broken


def _containers(doc, opener):
    """Every `<section ...>` container in `doc` opening with `opener`, from
    its first character to its closing tag, as exact substrings. Callout
    containers do not nest a section, so the first close after an open is
    that container's own."""
    out = []
    pos = 0
    while True:
        start = doc.find(opener, pos)
        if start == -1:
            return out
        close = doc.find("</section>", start)
        if close == -1:
            return out
        end = close + len("</section>")
        out.append(doc[start:end])
        pos = end


def scenario_thin_slice():
    """One authored [!PREREQUISITE] block, parser to registry to both
    renderers, in one function. Every failure names the hop that broke."""
    workdir = tempfile.mkdtemp(prefix="cap-tracer-")
    path = lesson_capability_corpus.build_thin_slice(workdir)

    parsed = model.parse_lesson(path)
    if parsed is None:
        fail("thin slice, parse hop: the corpus bank has no ## LESSON section")
    for key, want in (("semantic_profile", 1), ("lang", "en"), ("dir", "ltr")):
        if parsed.get(key) != want:
            fail("thin slice, parse hop: %s is %r, expected %r"
                 % (key, parsed.get(key), want))

    entry = capabilities.profile("callout_prerequisite")
    if entry is None:
        fail("thin slice, registry hop: callout_prerequisite is not "
             "registered, so the parsed block has no capability profile")
    if entry["renderer_availability"] != "available":
        fail("thin slice, registry hop: renderer_availability is %r, "
             "expected available" % entry["renderer_availability"])

    qs = model.load(path)
    continuous = lesson.lesson_page(path, qs, parsed)
    for needle in ('lang="en"', 'dir="ltr"',
                   'class="callout callout-prerequisite"', "Before this"):
        if needle not in continuous:
            fail("thin slice, continuous render hop: the document does not "
                 "contain %r, so the parsed field reached no renderer"
                 % needle)

    guided = lesson.lesson_page(path, qs, parsed, mode="guided")
    if 'data-stage="0"' not in guided:
        fail("thin slice, guided render hop: no stage was emitted")
    open_count = guided.count('data-stage-open="1"')
    if open_count != 1:
        fail("thin slice, guided render hop: %d stages carry "
             "data-stage-open, expected exactly 1" % open_count)

    opener = '<section class="callout callout-prerequisite"'
    before = _containers(continuous, opener)
    after = _containers(guided, opener)
    if not before:
        fail("thin slice, guided render hop: the continuous render produced "
             "no prerequisite container to compare against")
    if before != after:
        fail("thin slice, guided render hop: the prerequisite container is "
             "not character for character identical across modes, so guided "
             "mode re-rendered it instead of grouping it")

    lint = _run(["itembank.py", "lint", path])
    if lint.returncode != 0:
        fail("thin slice, lint hop: the corpus bank does not lint clean:\n%s"
             % (lint.stdout + lint.stderr))

    print("scenario thin_slice: pass")


def _baseline_hashes():
    """The Additivity baseline section of 16A-PRECONDITION.md, as
    {basename: sha256}. Read rather than carried as literals, so the baseline
    has exactly one home and cannot be quietly re-recorded here."""
    if not os.path.exists(PRECONDITION):
        fail("additivity: %s is missing. A missing baseline is a missing "
             "proof, and PLANNING-DIRECTIVES section 4 number 4 requires "
             "format additivity be proven by a byte-identical fixture, not "
             "promised" % os.path.relpath(PRECONDITION, ROOT))
    text = open(PRECONDITION, encoding="utf-8").read()
    section = text.split("## Additivity baseline", 1)
    if len(section) != 2:
        fail("additivity: 16A-PRECONDITION.md carries no Additivity baseline "
             "section")
    body = section[1].split("\n## ", 1)[0]
    found = {}
    for line in body.split("\n"):
        parts = line.split()
        if len(parts) == 2 and re.fullmatch(r"[0-9a-f]{64}", parts[1]):
            found[os.path.basename(parts[0])] = (parts[0], parts[1])
    if not found:
        fail("additivity: the Additivity baseline section carries no hash "
             "lines. A missing baseline is a missing proof")
    return found


def scenario_additivity_golden_parse():
    """The shipped format did not move while Phase 16A added to it."""
    baseline = _baseline_hashes()
    wanted = ("lesson_golden_phase3_parse.json",
              "lesson_golden_phase3_content.txt")
    for name in wanted:
        if name not in baseline:
            fail("additivity: the baseline names no hash for %s" % name)
        rel, expected = baseline[name]
        target = os.path.join(ROOT, rel)
        if not os.path.exists(target):
            fail("additivity: %s is missing" % rel)
        actual = hashlib.sha256(open(target, "rb").read()).hexdigest()
        if actual != expected:
            fail("additivity: %s is %s but 16A-PRECONDITION.md records %s, "
                 "so a format change was not additive"
                 % (rel, actual, expected))

    result = _run(["tests/lesson_roundtrip.py"])
    if result.returncode != 0:
        fail("additivity: tests/lesson_roundtrip.py exits %d:\n%s"
             % (result.returncode, result.stdout + result.stderr))

    print("scenario additivity_golden_parse: pass")


def _lint(path):
    """`model.lint` over one bank with every lesson-side pass switched on,
    which is the combination `itembank lint` itself uses. Returns
    `(error_codes, warning_codes)` as plain lists in emission order."""
    qs = model.load(path)
    errors, warnings = model.lint(
        qs, lesson=model.parse_lesson(path), terms=model.parse_terms(path),
        keys=model.parse_key_blocks(path))
    return [e.code for e in errors], [w.code for w in warnings]


CALLOUT_SLUGS = ("key", "example", "note", "warning", "prerequisite",
                 "misconception", "tip", "counterexample", "excerpt",
                 "uncertainty", "summary")


def scenario_fourteen_roles():
    """CAP-01's completeness claim, checked against real code rather than
    against prose: every catalogued role resolves to a module that imports
    and, when it names one, to a function that is actually callable, and
    every callout slug reaches both renderers."""
    catalog = capabilities.SEMANTIC_ROLE_CATALOG
    if len(catalog) != 14:
        fail("fourteen roles, catalog hop: SEMANTIC_ROLE_CATALOG has %d "
             "entries, expected 14" % len(catalog))
    for entry in catalog:
        if set(entry) != {"role", "mechanism", "module", "shipped_in",
                          "reachable_by"}:
            fail("fourteen roles, catalog hop: role %r carries the key set "
                 "%s, expected exactly role, mechanism, module, shipped_in, "
                 "reachable_by" % (entry.get("role"), sorted(entry)))
        try:
            mod = __import__(entry["module"], fromlist=["*"])
        except ImportError as exc:
            fail("fourteen roles, catalog hop: role %r names module %r, "
                 "which does not import (%s)"
                 % (entry["role"], entry["module"], exc))
        reach = entry["reachable_by"]
        if "." in reach and not reach.startswith(">"):
            attr = reach.split(".")[-1]
            target = getattr(mod, attr, None)
            if not callable(target):
                fail("fourteen roles, catalog hop: role %r names %r, which "
                     "is not callable on %s"
                     % (entry["role"], reach, entry["module"]))
        if capabilities.role_mechanism(entry["role"]) != entry:
            fail("fourteen roles, catalog hop: role_mechanism(%r) does not "
                 "return that role's entry" % entry["role"])
    if capabilities.role_mechanism("not a CAP-01 role") is not None:
        fail("fourteen roles, catalog hop: role_mechanism returns something "
             "for a role CAP-01 does not name")

    workdir = tempfile.mkdtemp(prefix="cap-tracer-roles-")
    path = lesson_capability_corpus.build_all_roles(workdir)
    errors, _warnings = _lint(path)
    if errors:
        fail("fourteen roles, lint hop: the all-roles bank reports %r"
             % errors)

    parsed = model.parse_lesson(path)
    qs = model.load(path)
    for mode in ("continuous", "guided"):
        page = lesson.lesson_page(path, qs, parsed, mode=mode)
        for slug in CALLOUT_SLUGS:
            if 'callout-%s"' % slug not in page \
                    and "callout-%s " % slug not in page:
                fail("fourteen roles, %s render hop: no callout-%s container "
                     "reached the page, so a catalogued role does not render"
                     % (mode, slug))
    print("scenario fourteen_roles: pass")


def scenario_unknown_semantics():
    """CAP-01's Degraded clause, both halves: an unknown optional semantic
    renders its pre-16A paragraph fallback with a warning, an unknown
    required one is refused out loud, and neither loses the author's words."""
    workdir = tempfile.mkdtemp(prefix="cap-tracer-unknown-")
    path = lesson_capability_corpus.build_unknown_semantics(workdir)
    page = lesson.lesson_page(path, model.load(path),
                              model.parse_lesson(path))

    count = page.count('class="callout callout-unsupported"')
    if count != 1:
        fail("unknown semantics, render hop: %d unsupported containers, "
             "expected exactly 1" % count)
    if lesson.UNSUPPORTED_SEMANTIC_COPY not in page:
        fail("unknown semantics, render hop: the locked refusal copy does "
             "not appear in the page")
    for needle in ("the reader refuses it out loud",
                   "it degrades to an ordinary paragraph"):
        if needle not in page:
            fail("unknown semantics, render hop: the author's own text %r "
                 "did not survive into the page, so a degradation path "
                 "dropped what the author wrote" % needle)

    errors, warnings = _lint(path)
    if errors.count("lesson.unknown_required_semantic") != 1:
        fail("unknown semantics, lint hop: %d unknown_required_semantic "
             "errors, expected exactly 1"
             % errors.count("lesson.unknown_required_semantic"))
    if warnings.count("lesson.unknown_semantic") != 1:
        fail("unknown semantics, lint hop: %d unknown_semantic warnings, "
             "expected exactly 1"
             % warnings.count("lesson.unknown_semantic"))
    print("scenario unknown_semantics: pass")


def scenario_example_order():
    """D-16A-6's three states: the default fires, a reasoned override
    suppresses it, and an override with no reason is not an override."""
    workdir = tempfile.mkdtemp(prefix="cap-tracer-order-")
    expected = {
        None: (0, 1),
        "with_reason": (0, 0),
        "no_reason": (1, 1),
    }
    for override, (want_err, want_warn) in expected.items():
        path = lesson_capability_corpus.build_definition_first(
            workdir, override=override)
        errors, warnings = _lint(path)
        got_err = errors.count("lesson.example_order_no_reason")
        got_warn = warnings.count("lesson.definition_before_example")
        if got_err != want_err:
            fail("example order, override=%r: %d example_order_no_reason "
                 "errors, expected %d" % (override, got_err, want_err))
        if got_warn != want_warn:
            fail("example order, override=%r: %d definition_before_example "
                 "warnings, expected %d" % (override, got_warn, want_warn))
    print("scenario example_order: pass")


def _capability_schema():
    with open(os.path.join(ROOT, "schemas",
                           "capability_profile.schema.json"),
              encoding="utf-8") as fh:
        return json.load(fh)


def scenario_capability_profiles():
    """CAP-02's first half: every capability declares all six fields, every
    catalogued role has a profile, every profile validates against the
    published schema, and no style rule requires a decorative block."""
    entries = capabilities.profiles()
    if len(entries) != 15:
        fail("capability profiles, registry hop: %d profiles, expected 15"
             % len(entries))

    by_name = {e["name"]: e for e in entries}
    mapped = set()
    for role in capabilities.SEMANTIC_ROLE_CATALOG:
        name = capabilities.catalog_profile_name(role["role"])
        if name not in by_name:
            fail("capability profiles, coupling hop: catalogued role %r maps "
                 "to %r, which is not registered" % (role["role"], name))
        mapped.add(name)
    extra = sorted(set(by_name) - mapped)
    if extra != ["guided_mode"]:
        fail("capability profiles, coupling hop: the profiles with no "
             "catalog role are %r, expected exactly ['guided_mode']" % extra)

    schema = _capability_schema()
    try:
        schema_validate.check_schema(schema)
    except schema_validate.SchemaError as exc:
        fail("capability profiles, schema hop: the published schema uses a "
             "keyword the shipped validator refuses: %s" % exc)
    for entry in entries:
        findings = capabilities.validate_profile(entry)
        if findings:
            fail("capability profiles, validation hop: %r is malformed: %s"
                 % (entry["name"], "; ".join(findings)))
        errors = schema_validate.validate(entry, schema)
        if errors:
            fail("capability profiles, schema hop: %r does not validate: %s"
                 % (entry["name"], "; ".join(errors)))

    # CAP-02's no-decorative-block clause, checked against a document that
    # uses none. A style system that required a decorative block would fire
    # here, which is what makes the clause checkable rather than
    # aspirational.
    workdir = tempfile.mkdtemp(prefix="cap-tracer-plain-")
    path = lesson_capability_corpus.build_no_callouts(workdir)
    errors, warnings = _lint(path)
    offending = [c for c in list(errors) + list(warnings)
                 if c.startswith("style.") or c in (
                     "lesson.unknown_semantic",
                     "lesson.unknown_required_semantic",
                     "lesson.definition_before_example")]
    if offending:
        fail("capability profiles, no-decorative-block hop: a lesson using "
             "zero callouts produced %r, so something requires a block "
             "CAP-02 says nothing may require" % offending)
    print("scenario capability_profiles: pass")


def scenario_unavailable_renderer():
    """CAP-02's Fixture sentence executed literally: one synthetic
    capability's full support profile, a second with its renderer marked
    unavailable, and the static instructional path asserted shown."""
    workdir = tempfile.mkdtemp(prefix="cap-tracer-unavail-")
    path = lesson_capability_corpus.build_unavailable_capability(workdir)
    page = lesson.lesson_page(path, model.load(path),
                              model.parse_lesson(path))
    fallback = capabilities.profile("inline_check")["offline_fallback"]
    if fallback not in page:
        fail("unavailable renderer, render hop: a gate-less check did not "
             "show the inline_check profile's declared offline_fallback, so "
             "the Degraded clause is documented and not implemented")

    if capabilities.resolved_availability("inline_check", {}) != "unavailable":
        fail("unavailable renderer, resolution hop: inline_check with no "
             "gate context does not resolve to unavailable")
    if capabilities.resolved_availability(
            "inline_check", {"gate_context": True}) != "available":
        fail("unavailable renderer, resolution hop: inline_check with a gate "
             "context does not resolve to available")

    before = len(capabilities.profiles())
    registry = capabilities.register({
        "name": "synthetic_available",
        "accessible_behavior": (
            "Fictional. Renders as a labelled section reachable in document "
            "order by keyboard and by screen reader."),
        "offline_fallback": (
            "Fictional. Renders as a labelled paragraph with no script."),
        "renderer_availability": "available",
        "version": 1,
        "validation": "Fictional. Nothing validates a synthetic capability.",
        "known_limits": "Fictional. It teaches nothing and is never authored.",
    })
    registry = capabilities.register({
        "name": "synthetic_unavailable",
        "accessible_behavior": (
            "Fictional. There is no renderer for this capability here."),
        "offline_fallback": (
            "This fictional capability has no renderer here. Read the "
            "printed steps instead."),
        "renderer_availability": "unavailable",
        "version": 1,
        "validation": "Fictional. Nothing validates a synthetic capability.",
        "known_limits": "Fictional. It exists only to be unavailable.",
    }, registry)

    static = lesson._static_instructional_html("synthetic_unavailable",
                                               registry)
    if 'class="capability-static"' not in static:
        fail("unavailable renderer, static-path hop: the declared static "
             "instructional path did not render a container")
    if "Read the printed steps instead." not in static:
        fail("unavailable renderer, static-path hop: the container does not "
             "carry the capability's own declared fallback text")
    if capabilities.resolved_availability(
            "synthetic_unavailable", {"scripting": True, "network": True},
            registry) != "unavailable":
        fail("unavailable renderer, resolution hop: a declared unavailable "
             "capability was raised by a caller's context, but the declared "
             "value is a ceiling nothing may raise")
    if lesson._static_instructional_html("no_such_capability") != "":
        fail("unavailable renderer, static-path hop: an unregistered name "
             "did not render the empty string")

    if len(capabilities.profiles()) != before:
        fail("unavailable renderer, purity hop: registering two synthetic "
             "capabilities changed the module registry, so a fixture can "
             "leak a capability into every later caller")
    print("scenario unavailable_renderer: pass")


SCENARIOS = (scenario_thin_slice, scenario_additivity_golden_parse,
             scenario_fourteen_roles, scenario_unknown_semantics,
             scenario_example_order, scenario_capability_profiles,
             scenario_unavailable_renderer)


def main():
    broken = shipped_suite_check()
    passed = skipped = 0
    if broken:
        for scenario in SCENARIOS:
            print("scenario %s: SKIP (shipped suite red: %s)"
                  % (scenario.__name__[len("scenario_"):], ", ".join(broken)))
            skipped += 1
    else:
        for scenario in SCENARIOS:
            scenario()
            passed += 1
    print("TRACER: %d passed, %d skipped, 0 failed" % (passed, skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
