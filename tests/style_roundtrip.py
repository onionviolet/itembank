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
import os, re, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import model                                                # noqa: E402
from model import (KEYS_UNCHECKED, LINT_CODES, LESSON_UNCHECKED,
                   LOCKED_RULE_IDS, STYLE_RULE_KINDS, STYLE_UNCHECKED,
                   TERMS_UNCHECKED, lint, load_style, resolve_style)  # noqa: E402


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
    print("\nstyle_roundtrip: ALL TESTS PASSED")


if __name__ == "__main__":
    main()
