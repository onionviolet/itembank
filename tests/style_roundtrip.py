#!/usr/bin/env python3
"""Roundtrip harness for the style registry (plan 03.1-04).

Standard library only, no test framework, runnable as
`python tests/style_roundtrip.py`.

Task 1 fixtures: the style loader's Voice/Rules/Exemplar parse, the
bank-adjacent -> user data dir -> bundled resolution order with the D-09
duplicate-id warning, the one-level inheritance guard
(`[STYLE-PARENT:]` != house is `style.parent_unknown`), and the code-owned
lock (`LOCKED_RULE_IDS` literal + `style.override_locked`).
"""
import json, os, re, shutil, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import model                                                # noqa: E402
from model import (KEYS_UNCHECKED, LINT_CODES, LESSON_UNCHECKED,
                   LOCKED_RULE_IDS, STYLE_RULE_KINDS, STYLE_UNCHECKED,
                   TERMS_UNCHECKED, StylePrompt, apply_style_ignore, lint,
                   load_style, resolve_style, run_style_pass,
                   style_manual_rules, style_suppression_report,
                   warning_ship_state, write_allowed)  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def check(name, cond, extra=""):
    if not cond:
        fail("%s%s" % (name, (" -- " + extra) if extra else ""))
    print("ok: " + name)


def codes(errors, warnings):
    return sorted({e.code for e in errors} | {w.code for w in warnings})


def style_text(rules, parent=""):
    parent_line = ("[STYLE-PARENT: %s]\n\n" % parent) if parent else ""
    rows = "\n".join("| %s |" % " | ".join(r) for r in rules)
    return (
        "# Style fixture\n\n"
        + parent_line
        + "## Voice\n\nWritten for the human maintainer, never sent to a model.\n\n"
        + "## Rules\n\n"
        + "| id | kind | params | severity | lock | prompt |\n"
        + "|----|------|--------|----------|------|--------|\n"
        + rows + "\n\n"
        + "## Exemplar\n\n### A heading\n\nProse in this style.\n")


def style_dict(rules, exemplar="Prose in this style.",
               voice="Voice prose for the human maintainer, never sent to a model."):
    """A parsed-style dict in `_parse_style_file`'s shape, built in memory --
    the fixtures for the content pass and the prompt compiler, which need a
    rules list, not a file on disk."""
    rows = []
    for r in rules:
        if isinstance(r, dict):
            rows.append(r)
        else:
            cells = (list(r) + ["", "", "", "", "", ""])[:6]
            rows.append({"id": cells[0], "kind": cells[1], "params": cells[2],
                         "severity": cells[3], "lock": cells[4],
                         "prompt": cells[5]})
    return {"id": "fixture", "path": "fixture", "voice": voice, "rules": rows,
            "exemplar": exemplar, "parent": "house", "warnings": [],
            "duplicate_rules": [], "error": "", "detail": ""}


def temp_tree():
    tmp = tempfile.mkdtemp(prefix="style_roundtrip_")
    bank = os.path.join(tmp, "bank")
    os.makedirs(os.path.join(bank, "styles"))
    user = os.path.join(tmp, "user")
    os.makedirs(user)
    return tmp, bank, user


def patch_user_data_dir(path):
    old = model._user_data_dir
    model._user_data_dir = lambda: path
    return old


def test_load_style_parses_voice_rules_exemplar():
    tmp, bank, _ = temp_tree()
    try:
        src = style_text([
            ("example-before-formal", "order.before", "[!EXAMPLE], [!KEY]",
             "error", "", "yes"),
            ("one-check-per-section", "style.require", "[!CHECK], 1",
             "error", "", "yes"),
            ("section-density", "density.max", "idea, 1", "warn", "", "no"),
        ], parent="house")
        # A fixture id that collides with no bundled style (the shipped
        # catalogue ships ids like expository/worked-example, and D-09's
        # duplicate warning is exactly what a same-id bank file must fire).
        with open(os.path.join(bank, "styles", "basic-fixture.md"), "w",
                  encoding="utf-8") as fh:
            fh.write(src)
        st = load_style("basic-fixture", bank)
        if st is None:
            fail("load_style returned None for an existing style file")
        check("load_style parses voice zone",
              "Written for the human maintainer" in st["voice"])
        check("load_style parses three rule rows", len(st["rules"]) == 3)
        check("rule row keeps id/kind/params/severity/lock/prompt",
              st["rules"][0] == {
                  "id": "example-before-formal", "kind": "order.before",
                  "params": "[!EXAMPLE], [!KEY]", "severity": "error",
                  "lock": "", "prompt": "yes"})
        check("load_style parses parent directive", st["parent"] == "house")
        check("load_style parses exemplar", "Prose in this style" in st["exemplar"])
        check("load_style finds no duplicate-level warning", st["warnings"] == [])

        # D-16: a row claiming a kind outside the closed set is
        # style.rule_unimplemented before the rule is ever applied.
        bad = dict(st)
        bad["rules"] = list(st["rules"]) + [{
            "id": "vibe", "kind": "magic.kind", "params": "",
            "severity": "error", "lock": "", "prompt": "yes"}]
        errs, warns = lint([], style=bad)
        check("unknown rule kind fires style.rule_unimplemented",
              "style.rule_unimplemented" in codes(errs, warns))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_resolution_order_and_duplicate_warning():
    tmp, bank, user = temp_tree()
    old = patch_user_data_dir(user)
    try:
        bank_file = os.path.join(bank, "styles", "resolve-fixture.md")
        user_file = os.path.join(user, "styles", "resolve-fixture.md")
        os.makedirs(os.path.join(user, "styles"))
        with open(bank_file, "w", encoding="utf-8") as fh:
            fh.write(style_text([("bank-row", "order.before", "A, B",
                                  "warn", "", "no")]))
        with open(user_file, "w", encoding="utf-8") as fh:
            fh.write(style_text([("user-row", "order.before", "A, B",
                                  "warn", "", "no")]))

        st = load_style("resolve-fixture", bank)
        if st is None:
            fail("load_style returned None when bank-adjacent file exists")
        check("bank-adjacent styles/ wins over user data dir",
              st["path"] == bank_file)
        check("duplicate id across levels warns naming both paths",
              any(bank_file in w and user_file in w
                  for w in st["warnings"]))

        os.remove(bank_file)
        st2 = load_style("resolve-fixture", bank)
        if st2 is None:
            fail("load_style returned None when user-level file exists")
        check("user data dir resolves when bank-adjacent is absent",
              st2["path"] == user_file)
        check("single match carries no duplicate warning", st2["warnings"] == [])

        # Absence returns None (D-09: resolution is by id, no silent shadow).
        check("load_style returns None when no level has the file",
              load_style("missing-style", bank) is None)
    finally:
        model._user_data_dir = old
        shutil.rmtree(tmp, ignore_errors=True)


def test_parent_unknown_and_one_inheritance_level():
    tmp, bank, _ = temp_tree()
    try:
        bad_parent = style_text([("row", "open.with", "paragraph",
                                  "warn", "", "no")], parent="worked-example")
        p = os.path.join(bank, "styles", "child.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(bad_parent)
        st = load_style("child", bank)
        if st is None:
            fail("load_style returned None for parent fixture")
        errs, warns = lint([], style=st)
        check("[STYLE-PARENT:] other than house is style.parent_unknown",
              "style.parent_unknown" in codes(errs, warns))

        ok_parent = style_text([("row", "open.with", "paragraph",
                                 "warn", "", "no")], parent="house")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(ok_parent)
        st2 = load_style("child", bank)
        errs2, warns2 = lint([], style=st2)
        check("parent house is legal", "style.parent_unknown"
              not in codes(errs2, warns2))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_locked_rule_ids_literal_and_override():
    src = open(os.path.join(ROOT, "model.py"), encoding="utf-8").read()
    check("LOCKED_RULE_IDS is a literal frozenset in model.py",
          bool(re.search(r"LOCKED_RULE_IDS\s*=\s*frozenset\(\{", src)))
    check("STYLE_RULE_KINDS is a literal frozenset in model.py",
          bool(re.search(r"STYLE_RULE_KINDS\s*=\s*frozenset\(\{", src)))
    check("LOCKED_RULE_IDS is non-empty", len(LOCKED_RULE_IDS) >= 5)
    check("all locked ids are code-side kinds",
          all(isinstance(x, str) and "." in x for x in LOCKED_RULE_IDS))

    tmp, bank, _ = temp_tree()
    try:
        locked_id = sorted(LOCKED_RULE_IDS)[0]
        # Any severity -- including off -- is an override attempt.
        for severity in ("warn", "error", "off"):
            src_text = style_text([
                (locked_id, "house.mandate", "", severity, "yes", "no")],
                parent="house")
            p = os.path.join(bank, "styles", "child.md")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(src_text)
            st = load_style("child", bank)
            if st is None:
                fail("load_style returned None for locked-row fixture")
            errs, warns = lint([], style=st)
            cs = codes(errs, warns)
            check("child row naming locked id at severity %s is "
                  "style.override_locked" % severity,
                  "style.override_locked" in cs, str(cs))

        # A style row carrying a lock cell at all is style.ignore_locked:
        # only code may manage locks (T-031-12).
        src_text = style_text([
            ("ordinary-rule", "style.require", "[!CHECK], 1", "error",
             "no", "yes")], parent="house")
        p = os.path.join(bank, "styles", "child.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(src_text)
        st = load_style("child", bank)
        errs, warns = lint([], style=st)
        check("non-house row managing a lock is style.ignore_locked",
              "style.ignore_locked" in codes(errs, warns))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_resolve_style_precedence():
    tmp, bank, _ = temp_tree()
    try:
        for sid in ("expository", "worked-example", "checked-prose"):
            with open(os.path.join(bank, "styles", sid + ".md"), "w",
                      encoding="utf-8") as fh:
                fh.write(style_text([("row", "open.with", "paragraph",
                                      "warn", "", "no")], parent="house"))
        bank_file = os.path.join(bank, "bank.md")

        def write_bank(preamble_style="", lesson_style=""):
            lines = ["# Fixture bank", ""]
            if preamble_style:
                lines += ["[STYLE: %s]" % preamble_style, ""]
            lines += ["## LESSON", ""]
            if lesson_style:
                lines += ["[STYLE: %s]" % lesson_style, ""]
            lines += ["### A heading", "", "Prose.", ""]
            with open(bank_file, "w", encoding="utf-8") as fh:
                fh.write("\n".join(lines))

        # lesson beats bank
        write_bank(preamble_style="expository", lesson_style="worked-example")
        r = resolve_style([], bank_file, {})
        check("lesson-level [STYLE:] beats bank-level",
              r["id"] == "worked-example" and r["level"] == "lesson")

        # bank beats subject profile
        write_bank(preamble_style="expository")
        r = resolve_style([], bank_file, {"styles": {"subject_default":
                                                     "checked-prose"}})
        check("bank-level [STYLE:] beats subject profile",
              r["id"] == "expository" and r["level"] == "bank")

        # subject profile beats house
        write_bank()
        r = resolve_style([], bank_file, {"styles": {"subject_default":
                                                     "checked-prose"}})
        check("subject profile default beats house",
              r["id"] == "checked-prose" and r["level"] == "subject")

        # house is the guaranteed fallback
        write_bank()
        r = resolve_style([], bank_file, {})
        check("house is the fallback when nothing names a style",
              r["id"] == "house" and r["level"] == "house")

        # a directive naming an absent style resolves with style None so lint
        # can report style.file_unreadable
        write_bank(lesson_style="no-such-style")
        r = resolve_style([], bank_file, {})
        check("missing style resolves id with style None",
              r["id"] == "no-such-style" and r["style"] is None)
        errs, warns = lint([], style=r["style"])
        check("missing resolved style fires style.file_unreadable",
              "style.file_unreadable" in codes(errs, warns))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_shipped_styles_load_and_lint_clean():
    """All five shipped styles plus house resolve through load_style()'s
    bundled level with a ## Voice zone, a ## Rules pipe table and an
    ## Exemplar; every rule row's kind is inside the closed STYLE_RULE_KINDS
    set (D-16), and a lint pass over each resolved style emits no style.*
    finding (plan 03.1-04 Task 2 acceptance: five styles load and lint
    clean under D-16)."""
    tmp, _, _ = temp_tree()
    old = patch_user_data_dir(os.path.join(tmp, "empty-user"))
    try:
        for sid in ("house", "expository", "worked-example", "checked-prose",
                    "artifact-first", "case-narrative"):
            st = load_style(sid, None)
            if st is None or st.get("error"):
                fail("bundled style %r did not resolve at the bundled level "
                     "(D-09)" % sid)
            check("%s carries a ## Voice zone" % sid,
                  bool(st["voice"].strip()))
            check("%s carries a ## Rules table" % sid,
                  len(st["rules"]) >= 2)
            check("%s carries an ## Exemplar" % sid,
                  bool(st["exemplar"].strip()))
            bad = [r["id"] for r in st["rules"]
                   if r.get("kind") not in STYLE_RULE_KINDS]
            check("%s rule kinds are all in the closed set (D-16)" % sid,
                  not bad, repr(bad))
            errs, warns = lint([], style=st)
            style_findings = [e for e in errs + warns
                              if e.code.startswith("style.")]
            check("%s lints clean under D-16" % sid,
                  not style_findings,
                  repr([str(e) for e in style_findings]))
    finally:
        model._user_data_dir = old
        shutil.rmtree(tmp, ignore_errors=True)


def test_style_parents_predict_flag_and_house_documents_locks():
    """The declared inheritance contract: expository is the content parent
    and declares no machine [STYLE-PARENT:] directive, the other four
    declare the exactly-one-level machine parent `house` (D-10 -- a
    [STYLE-PARENT:] naming anything but house is style.parent_unknown), and
    name expository as their content parent; checked-prose carries the
    predict_first flag (D-08); styles/house.md documents every
    LOCKED_RULE_IDS id in prose but never defines them (ruling 13)."""
    bundled = {}
    for sid in ("house", "expository", "worked-example", "checked-prose",
                "artifact-first", "case-narrative"):
        st = load_style(sid, None)
        if st is None or st.get("error"):
            fail("bundled style %r unavailable for the parent fixture" % sid)
        bundled[sid] = st
    check("expository declares no [STYLE-PARENT:] directive",
          bundled["expository"]["parent"] == "")
    for sid in ("worked-example", "checked-prose", "artifact-first",
                "case-narrative"):
        st = bundled[sid]
        check("%s declares the one-level machine parent house (D-10)" % sid,
              st["parent"] == "house")
        check("%s names expository as its content parent" % sid,
              "expository" in st["voice"] + st["exemplar"])
    checked = bundled["checked-prose"]
    check("checked-prose carries the predict_first flag (D-08)",
          "predict_first" in checked["voice"] + checked["exemplar"])
    house_text = bundled["house"]["voice"] + bundled["house"]["exemplar"]
    for locked in sorted(LOCKED_RULE_IDS):
        check("house.md documents locked id %s" % locked,
              locked in house_text)


def test_rule6_stub_one_file_extensibility():
    """Extensibility Rule 6 (03.1-UI-SPEC 17.8): a throwaway sixth style
    file added to a bank-adjacent styles/ dir loads through the existing
    loader and lints clean with no parser, lint-code, or renderer change --
    the test writes only the new file, which is the whole proof."""
    tmp, bank, _ = temp_tree()
    try:
        sixth = style_text([
            ("stub.order", "order.before", "[!EXAMPLE], [!KEY]",
             "warn", "", "no")], parent="house")
        with open(os.path.join(bank, "styles", "sixth.md"), "w",
                  encoding="utf-8") as fh:
            fh.write(sixth)
        st = load_style("sixth", bank)
        if st is None:
            fail("a sixth style file did not load through load_style")
        errs, warns = lint([], style=st)
        check("Rule 6 stub lints clean with zero code change",
              not [e for e in errs + warns if e.code.startswith("style.")])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_stage_dirs_allowlist_ships_styles():
    """The artifact's bundled styles/ directory enters the release only
    through build.py's STAGE_DIRS allowlist (T-031-SC) -- the same explicit
    allowlist that keeps learner evidence and private banks out."""
    src = open(os.path.join(ROOT, "build.py"), encoding="utf-8").read()
    m = re.search(r"STAGE_DIRS\s*=\s*\(([^)]*)\)", src)
    if not m:
        fail("build.py has no STAGE_DIRS allowlist tuple")
    names = [n.strip().strip("'\"") for n in m.group(1).split(",")]
    check("styles/ is in build.py's STAGE_DIRS allowlist",
          "styles" in names, repr(names))


def test_render_style_permutes_and_refuses():
    """Task 3 Test 2: render_style permutes only existing blocks per the
    target style's order.before rules and refuses each of the five named
    D-11 transforms with the exact copy, writing no file on refusal
    (03.1-UI-SPEC 9.6, ROADMAP 3b)."""
    from surfaces import lesson as lesson_mod
    tmp, bank, _ = temp_tree()
    try:
        with open(os.path.join(bank, "styles", "worked-example.md"), "w",
                  encoding="utf-8") as fh:
            fh.write(style_text([
                ("example.before.variation", "order.before",
                 "[!EXAMPLE], [!KEY]", "error", "", "yes"),
            ], parent="house"))

        def write_bank(style_id, body_lines):
            lines = ["# Fixture bank", ""]
            if style_id:
                lines += ["[STYLE: %s]" % style_id, ""]
            lines += ["## LESSON", ""] + body_lines + [
                "", "Q1. s", "A) a", "B) b", "CORRECT: A", ""]
            p = os.path.join(bank, "bank.md")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write("\n".join(lines))
            return p

        # checked-prose -> worked-example is a legal permutation (not one
        # of the five named refusals), and the target's order.before rule
        # must move the [!EXAMPLE] ahead of the [!KEY] inside the section.
        bank_file = write_bank("checked-prose", [
            "### A heading", "", "Prose that introduces the idea.", "",
            "> [!KEY] The rule to remember.", "",
            "> [!EXAMPLE] A worked instance.", ""])
        out = os.path.join(tmp, "permuted.html")
        result = lesson_mod.render_style(bank_file, "worked-example", out=out)
        if not os.path.exists(out):
            fail("render_style wrote no output file: %r" % (result,))
        html = open(out, encoding="utf-8").read()
        key_pos = html.find('class="callout callout-key"')
        ex_pos = html.find('class="callout callout-example"')
        check("order.before permutes [!EXAMPLE] ahead of [!KEY]",
              0 <= ex_pos < key_pos, (ex_pos, key_pos))
        check("rendered page carries the style footer",
              "style: worked-example \u00b7 rendered by render_style"
              in html)

        # The five named refusals fire with the exact copy and write
        # nothing (D-11): expository->case-narrative, expository->Socratic,
        # expository->worked-example, anything->Bottom-Up, and
        # case-narrative->anything.
        cases = [
            ("expository", "case-narrative"),
            ("expository", "socratic"),
            ("expository", "worked-example"),
            ("checked-prose", "artifact-first"),
            ("case-narrative", "expository"),
        ]
        for src, tgt in cases:
            write_bank(src, ["### A heading", "", "Prose.", "",
                             "> [!KEY] A key.", ""])
            out2 = os.path.join(tmp, "refused-%s-%s.html" % (src, tgt))
            res = lesson_mod.render_style(bank_file, tgt, out=out2)
            expected = ("render_style cannot turn %s into %s; that is a "
                        "rewrite, not a rearrangement. No file was changed."
                        % (src, tgt))
            check("%s->%s refuses with the exact copy" % (src, tgt),
                  res == expected, repr(res))
            check("no file written on refusal",
                  not os.path.exists(out2))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_render_style_cli_registered():
    """The render_style CLI seam is registered (plan 03.1-04 Task 3): the
    command exists with --style/--out and prints usage, so an authoring
    agent can reach the refusal copy without a route."""
    res = subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"),
         "render-style", "--help"],
        capture_output=True, text=True)
    if res.returncode != 0:
        fail("render-style --help failed: " + res.stdout + res.stderr)
    check("render-style CLI is registered and documented",
          "--style" in res.stdout and "--out" in res.stdout)


def test_render_style_has_no_model_client():
    """Task 3 Test 3: render_style is structurally model-free -- its
    signature cannot accept a model client and an AST walk of its body
    names no model-adapter symbol (D-11, Directive 4.1)."""
    import ast
    import inspect
    from surfaces import lesson as lesson_mod
    sig = inspect.signature(lesson_mod.render_style)
    if {"model", "client", "adapter", "llm"} & set(sig.parameters):
        fail("render_style's signature must not accept a model client")
    tree = ast.parse(inspect.getsource(lesson_mod.render_style))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
    banned = {"model_client", "client", "adapter", "llm", "chat",
              "complete", "generate", "openai", "anthropic"}
    hit = names & banned
    check("render_style names no model-client symbol", not hit,
          repr(sorted(hit)))


# ---- plan 03.1-05 Task 1: three cost classes, closed catalogue, D-15 -------


def _style_doc(rules, voice="## Voice\n\nTeach with judgement.",
               exemplar="## Exemplar\n\nA short worked case."):
    return {"rules": rules, "voice": voice, "exemplar": exemplar}


def _lesson_doc(body, sections=()):
    return {"body": body,
            "headings": [{"text": t, "slug": model.lesson_slug(t), "body": b}
                         for t, b in sections]}


def test_three_cost_classes_fire_and_manual_defers():
    """Task 1 Test 1 (D-12): the structural class (require_marker,
    forbidden_marker, order_before) and the one shared lexical class
    (sentence_length, filler_phrase, banned_hector) both fire on one lint;
    a discourse row declared `manual` is listed by style_manual_rules and
    never fabricated into a check."""
    st = _style_doc([
        {"id": "scenario.required", "kind": "style.require",
         "params": "## SCENARIO, 1", "severity": "error", "prompt": "yes"},
        {"id": "narrative.holds", "kind": "style.forbid",
         "params": "[!KEY]", "severity": "warn", "prompt": "no"},
        {"id": "reveal.sequential", "kind": "order.before",
         "params": "[!CHECK], [!KEY]", "severity": "warn", "prompt": "no"},
        {"id": "discourse.judgement", "kind": "style.require",
         "params": "## SCENARIO, 2", "severity": "manual", "prompt": "yes"},
    ])
    long = ("This is a deliberately long sentence that keeps adding words "
            "until it crosses the twenty eight word ceiling of the shared "
            "lexical pass for sure and continues beyond that limit without "
            "stopping")
    body = ("## The case\n\n%s.\n\nBasically, you must remember this point.\n\n"
            "[!KEY: k1] then [!CHECK: c1]\n" % long)
    lesson = _lesson_doc(body, [("## The case",
                                 "%s.\n\nBasically, you must remember this point.\n\n"
                                 "[!KEY: k1] then [!CHECK: c1]" % long)])
    errs, warns = run_style_pass(lesson, st)
    got = {e.code for e in errs} | {w.code for w in warns}
    check("structural class fires require_marker", "style.require_marker" in got)
    check("structural class fires forbidden_marker", "style.forbidden_marker" in got)
    check("structural class fires order_before", "style.order_before" in got)
    check("lexical class fires sentence_length", "style.sentence_length" in got)
    check("lexical class fires filler_phrase", "style.filler_phrase" in got)
    check("lexical class fires banned_hector", "style.banned_hector" in got)
    check("manual rows listed, never fabricated",
          style_manual_rules(st) == ["discourse.judgement"]
          and sum(1 for e in errs if e.code == "style.require_marker") == 1)


def test_severity_ceiling_disable_and_parameterize():
    """Task 1 Test 2 (D-13): a style may disable a check, re-severity it
    downward, or parameterize it, but never raise it above the catalogue
    rating (style.parameter_out_of_range); an unknown severity cell is
    style.unknown_parameter."""
    st_raise = _style_doc([{"id": "style.sentence_length", "kind": "density.max",
                            "params": "style.sentence_length", "severity": "error"}])
    errs, warns = run_style_pass(_lesson_doc("A short clean prose body."), st_raise)
    check("raising a warn check to error is style.parameter_out_of_range",
          any(e.code == "style.parameter_out_of_range" for e in errs))
    long = ("This sentence crosses the twenty eight word ceiling of the shared "
            "lexical pass for sure and keeps going well beyond the limit "
            "without stopping at all")
    st_off = _style_doc([{"id": "style.sentence_length", "kind": "density.max",
                          "params": "style.sentence_length", "severity": "off"}])
    errs, warns = run_style_pass(_lesson_doc("## S\n\n%s.\n" % long,
                                             [("## S", "%s." % long)]), st_off)
    check("a style may disable a check",
          not any(e.code == "style.sentence_length" for e in errs + warns))
    st_tight = _style_doc([{"id": "style.sentence_length", "kind": "density.max",
                            "params": "style.sentence_length, max=5", "severity": "warn"}])
    errs, warns = run_style_pass(_lesson_doc("## S\n\na seven word sentence here exceeds the cap.\n",
                                             [("## S", "a seven word sentence here exceeds the cap.")]),
                                 st_tight)
    check("parameterizing the ceiling tightens the check",
          any(w.code == "style.sentence_length" for w in warns))
    st_bad = _style_doc([{"id": "r1", "kind": "style.require",
                          "params": "## X, 1", "severity": "banana"}])
    errs, warns = run_style_pass(_lesson_doc("## X\n\ntext."), st_bad)
    check("unknown severity cell is style.unknown_parameter",
          any(e.code == "style.unknown_parameter" for e in errs))


def test_write_allowed_blocks_machine_write_never_human_lint():
    """Task 1 Test 3 (D-15): a style error blocks a machine-authored write
    (write_allowed refuses) and never a human's lint -- lint() still returns
    the full diagnosis and keeps the pen."""
    st = _style_doc([{"id": "scenario.required", "kind": "style.require",
                      "params": "## SCENARIO, 1", "severity": "error"}])
    lesson = _lesson_doc("## The case\n\nA short body with no scenario at all.",
                         [("## The case", "A short body with no scenario at all.")])
    errs, warns = run_style_pass(lesson, st)
    check("write_allowed refuses a style error", not write_allowed(st, errs + warns))
    e2, w2 = lint([], lesson=lesson, style=st)
    diag = [x for x in e2 + w2 if x.code.startswith("style.")]
    check("human lint still returns the style diagnosis",
          any(x.code == "style.require_marker" for x in diag))


# ---- plan 03.1-05 Task 2: suppression, calibration, 50ms budget ------------


def test_suppression_counts_and_report():
    """Task 2 Test 1 (D-14): `<!-- style-ignore: code -->` suppresses a
    non-locked warning, the suppression is counted, and the report lists
    code, count, and lesson line locations."""
    st = _style_doc([])
    body = ("<!-- style-ignore: style.filler_phrase -->\n\n"
            "Basically, this prose uses a filler phrase right here.")
    lesson = _lesson_doc(body, [("## One",
                                 "Basically, this prose uses a filler phrase right here.")])
    errs, warns = run_style_pass(lesson, st)
    check("the filler warning fires pre-suppression",
          any(w.code == "style.filler_phrase" for w in warns))
    kept, counts, ignore_errors = apply_style_ignore(warns, body)
    check("non-locked warning is suppressed",
          not any(w.code == "style.filler_phrase" for w in kept))
    check("suppression is counted", counts.get("style.filler_phrase") == 1)
    rep = style_suppression_report(body)
    check("report lists code, count, and locations",
          any(r["code"] == "style.filler_phrase" and r["count"] == 1
              and r["locations"] == [1] for r in rep))


def test_locked_suppression_is_itself_an_error():
    """Task 2 Test 2 (T-031-19): suppressing a LOCKED_RULE_IDS id is itself
    lint error style.ignore_locked and never suppresses the finding."""
    findings = [model.LintError("runtime.decides", "lesson", "BANK",
                                "locked house finding")]
    kept, counts, ignore_errors = apply_style_ignore(
        findings, "<!-- style-ignore: runtime.decides -->")
    check("locked finding still stands",
          [f.code for f in kept] == ["runtime.decides"])
    check("the attempt is style.ignore_locked",
          any(e.code == "style.ignore_locked" for e in ignore_errors))
    check("nothing was suppressed", counts == {})


def test_50ms_budget_on_5000_word_lesson():
    """Task 2 Test 3 (T-031-18): the whole style pass stays under 50ms on a
    synthetic 5000-word lesson, measured with time.perf_counter() and the
    measured time printed in the output line (D-12)."""
    words = ("the quick brown fox jumps over the lazy dog and keeps moving "
             "through the lesson prose without any filler or hector wording ")
    body = "## Section\n\n" + (words * 300)
    lesson = _lesson_doc(body, [("## Section", body)])
    st = _style_doc([])
    t0 = time.perf_counter()
    errs, warns = run_style_pass(lesson, st)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    check("style pass on a 5000-word lesson stays under 50ms",
          elapsed_ms < 50.0, "%.2f ms" % elapsed_ms)
    print("ok: style pass on ~5100-word lesson ran in %.2f ms" % elapsed_ms)


def test_warning_ship_state_calibrated_by_fp_rate():
    """Task 2 Test 4 (D-14): a warning's ship-state derives from its recorded
    false-positive rate; above WARNING_FP_THRESHOLD it ships disabled by
    default, and the rate is recorded beside the code."""
    over = warning_ship_state("style.filler_phrase", 0.5)
    under = warning_ship_state("style.filler_phrase", 0.10)
    bare = warning_ship_state("style.filler_phrase")
    check("above 0.20 ships disabled with the rate recorded",
          over["ship_state"] == "disabled" and over["fp_rate"] == 0.5)
    check("at or below 0.20 ships enabled", under["ship_state"] == "enabled")
    check("no recorded rate ships enabled on the open seam",
          bare["ship_state"] == "enabled" and bare["fp_rate"] is None)
    check("the threshold constant is 0.20", model.WARNING_FP_THRESHOLD == 0.20)


# ---- plan 03.1-05 Task 3: StylePrompt.prompt_context + settings group ------


def _prompt_style(n_rules):
    return {"rules": [{"id": "r%d" % i, "kind": "style.require",
                       "params": "## S%d, 1" % i, "severity": "warn",
                       "prompt": "yes"} for i in range(n_rules)],
            "voice": "## Voice\n\nThe quiet authority of a clinician at the bedside.",
            "exemplar": "## Exemplar\n\nThe ideal worked case follows every imperative above."}


def _imperative_lines(ctx):
    return [ln for ln in ctx.splitlines() if ln.startswith("- ")]


def test_prompt_context_capped_imperatives_one_exemplar_no_voice():
    """Task 3 Test 1 (D-17): prompt_context returns the capped imperative
    set, exactly one exemplar, and zero ## Voice prose -- the voice zone
    never reaches the model (fixture greps assert its absence)."""
    ctx = StylePrompt.prompt_context(_prompt_style(10))
    check("cap defaults to 7 imperatives",
          len(_imperative_lines(ctx)) == 7, repr(_imperative_lines(ctx)))
    check("exactly one exemplar content block",
          ctx.count("The ideal worked case follows every imperative above.") == 1)
    check("voice prose is never emitted", "quiet authority" not in ctx)


def test_imperatives_and_exemplar_are_last():
    """Task 3 Test 2: the imperatives and the exemplar are the final blocks
    of the returned context -- last position is the finding, not taste."""
    ctx = StylePrompt.prompt_context(_prompt_style(3))
    check("exemplar text is the final block",
          ctx.rstrip().endswith("The ideal worked case follows every imperative above."))
    check("imperatives precede the exemplar",
          ctx.index("## Style requirements") < ctx.index("## Exemplar"))


def test_cap_is_a_settings_value():
    """Task 3 Test 3: the cap is a setting -- changing it changes the emitted
    count without a code change; the default constant is 7."""
    st = _prompt_style(10)
    check("cap=2 emits two imperatives",
          len(_imperative_lines(StylePrompt.prompt_context(st, 2))) == 2)
    check("cap=0 emits no imperatives",
          len(_imperative_lines(StylePrompt.prompt_context(st, 0))) == 0)
    check("cap=9 clamps to the available rules",
          len(_imperative_lines(StylePrompt.prompt_context(st, 9))) == 9)
    check("the default cap constant is 7", StylePrompt.DEFAULT_CAP == 7)


def test_style_settings_group_validates_and_shows_in_config():
    """Task 3 Test 4: the style settings group validates through itembank
    config (validate-then-write) and appears in `itembank config` output."""
    schema = json.load(open(os.path.join(ROOT, "schemas", "settings.schema.json"),
                            encoding="utf-8"))
    group = schema["properties"]["style"]
    check("style group carries the cap default and phase",
          group["default"]["imperative_cap"] == 7
          and group["x-itembank-phase"] == 3.1)
    from surfaces.settings import style_defaults
    check("style_defaults exposes the group",
          style_defaults()["imperative_cap"] == 7
          and style_defaults()["warn_fp_threshold"] == 0.20)
    out = subprocess.run([sys.executable, os.path.join(ROOT, "itembank.py"), "config"],
                         capture_output=True, text=True, cwd=ROOT).stdout
    check("`itembank config` output names the style group", "style" in out)


def main():
    test_load_style_parses_voice_rules_exemplar()
    test_resolution_order_and_duplicate_warning()
    test_parent_unknown_and_one_inheritance_level()
    test_locked_rule_ids_literal_and_override()
    test_resolve_style_precedence()
    test_shipped_styles_load_and_lint_clean()
    test_style_parents_predict_flag_and_house_documents_locks()
    test_rule6_stub_one_file_extensibility()
    test_stage_dirs_allowlist_ships_styles()
    test_render_style_permutes_and_refuses()
    test_render_style_cli_registered()
    test_render_style_has_no_model_client()
    test_three_cost_classes_fire_and_manual_defers()
    test_severity_ceiling_disable_and_parameterize()
    test_write_allowed_blocks_machine_write_never_human_lint()
    test_suppression_counts_and_report()
    test_locked_suppression_is_itself_an_error()
    test_50ms_budget_on_5000_word_lesson()
    test_warning_ship_state_calibrated_by_fp_rate()
    test_prompt_context_capped_imperatives_one_exemplar_no_voice()
    test_imperatives_and_exemplar_are_last()
    test_cap_is_a_settings_value()
    test_style_settings_group_validates_and_shows_in_config()
    print("\nstyle_roundtrip: ALL TESTS PASSED")


if __name__ == "__main__":
    main()
