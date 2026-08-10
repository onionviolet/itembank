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
        with open(os.path.join(bank, "styles", "expository.md"), "w",
                  encoding="utf-8") as fh:
            fh.write(src)
        st = load_style("expository", bank)
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
        bank_file = os.path.join(bank, "styles", "expository.md")
        user_file = os.path.join(user, "styles", "expository.md")
        os.makedirs(os.path.join(user, "styles"))
        with open(bank_file, "w", encoding="utf-8") as fh:
            fh.write(style_text([("bank-row", "order.before", "A, B",
                                  "warn", "", "no")]))
        with open(user_file, "w", encoding="utf-8") as fh:
            fh.write(style_text([("user-row", "order.before", "A, B",
                                  "warn", "", "no")]))

        st = load_style("expository", bank)
        if st is None:
            fail("load_style returned None when bank-adjacent file exists")
        check("bank-adjacent styles/ wins over user data dir",
              st["path"] == bank_file)
        check("duplicate id across levels warns naming both paths",
              any(bank_file in w and user_file in w
                  for w in st["warnings"]))

        os.remove(bank_file)
        st2 = load_style("expository", bank)
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


def main():
    test_load_style_parses_voice_rules_exemplar()
    test_resolution_order_and_duplicate_warning()
    test_parent_unknown_and_one_inheritance_level()
    test_locked_rule_ids_literal_and_override()
    test_resolve_style_precedence()
    print("\nstyle_roundtrip: ALL TESTS PASSED")


if __name__ == "__main__":
    main()
