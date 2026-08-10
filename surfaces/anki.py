"""Anki TSV export: Basic and Cloze, generic to any bank.

Subject-specific packaging (Mandarin TTS, `.apkg` building) stays out, because
it needs dependencies and network access that this tool refuses to grow.
"""
import os, re, sys

from model import lint, load, parse_key_blocks, parse_lesson, parse_terms
from runtime import answer_text
from surfaces import gift


def tsv_cell(value):
    return re.sub(r"\s+", " ", str(value or "")).replace("\t", " ").strip()


_CLOZE_MARK_RE = re.compile(r"\{\{([^{}]+)\}\}")


def _render_cloze_text(text):
    """The on-screen form of a key body: `{{...}}` markers render as their
    enclosed text (03.1-UI-SPEC §9.2); blanking happens only in the drill
    print sheet."""
    return _CLOZE_MARK_RE.sub(lambda m: m.group(1), text)


def _compile_cloze(text):
    """Compile authored cloze markers to Anki's native cloze syntax for the
    Cloze notetype: `{{text}}` becomes `{{c1::text}}` with sequential
    numbering, and a numbered `{{n::text}}` keeps its number."""
    counter = [0]

    def _rep(m):
        inner = m.group(1)
        if "::" in inner:
            num, content = inner.split("::", 1)
            return "{{c%s::%s}}" % (num.strip(), content)
        counter[0] += 1
        return "{{c%d::%s}}" % (counter[0], inner)

    return _CLOZE_MARK_RE.sub(_rep, text)


def export_keys(bank, force=False):
    """The [!KEY] path of the Anki exporter (03.1-03 Task 2, LESSON-08): a
    multi-directive TSV whose #guid column carries each block's minted
    [ID:] -- Anki's documented update-by-guid semantics, so re-export after
    a body edit is an update, never a duplicate.

    Reads only the lesson machinery (`parse_lesson()` + `parse_key_blocks()`
    + the terms/key lint pass) -- never `load()`/`parse_bank()` -- and
    refuses a bank whose key blocks carry errors without `--force`, matching
    the item export's contract.
    """
    lesson = parse_lesson(bank)
    keys = parse_key_blocks(bank)
    if not keys:
        sys.exit("no [!KEY] blocks found in %s" % bank)
    errors, _ = lint([], lesson=lesson, terms=parse_terms(bank), keys=keys)
    if errors and not force:
        for e in errors:
            print("error  " + str(e))
        sys.exit("refusing to export a bank with key errors; fix them or "
                 "pass --force")
    stem = os.path.splitext(os.path.basename(bank))[0]
    out = os.path.join(os.path.dirname(os.path.abspath(bank)),
                       stem + "_keys.tsv")
    rows = []
    for key in keys:
        tags = "itembank"
        if key.get("section_slug"):
            tags += " " + key["section_slug"]
        if key.get("cloze"):
            notetype = "Cloze"
            front = _compile_cloze(key["body"])
            back = ""
        else:
            notetype = "Basic"
            front = key.get("title", "")
            back = _render_cloze_text(key["body"])
        rows.append("%s\t%s\t%s\t%s\t%s\t%s" % (
            tsv_cell(key.get("id")), notetype, tsv_cell(stem),
            tsv_cell(front), tsv_cell(back), tags))
    header = ["#separator:tab", "#html:true", "#guid column:1",
              "#notetype column:2", "#deck column:3", "#tags column:6",
              "Guid\tNotetype\tDeck\tFront\tBack\tTags"]
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w", encoding="utf-8").write("\n".join(header + rows) + "\n")
    print("%d keys -> %s" % (len(keys), out))
    return out


def cmd_export(a):
    if a.format == "gift":
        return gift.export_gift(a)
    if a.format == "keys":
        export_keys(a.bank, force=a.force)
        return 0
    if not a.out:
        sys.exit("usage: itembank export BANK OUT --format basic|cloze|gift")
    qs = load(a.bank)
    errors, _ = lint(qs)
    if errors and not a.force:
        sys.exit("refusing to export a bank with errors; fix them or pass --force")
    rows = []
    for q in qs:
        front = q["stem"]
        answer = answer_text(q)
        if a.format == "cloze":
            text = "%s {{c1::%s}}" % (front, answer)
            rows.append("%s\t%s" % (tsv_cell(text), tsv_cell(q.get("why") or q.get("disc"))))
        else:
            options = ""
            if q["type"] in ("mc", "multi"):
                options = " Options: " + " | ".join("%s) %s" % (k, q["opts"][k]) for k in sorted(q["opts"]))
            rows.append("%s\t%s%s" % (tsv_cell(front + options), tsv_cell(answer),
                                       ("<br><br>" + tsv_cell(q.get("why"))) if q.get("why") else ""))
    header = ["#separator:tab", "#html:true"]
    if a.format == "cloze":
        header += ["#notetype:Cloze", "Text\tExtra"]
    else:
        header += ["#notetype:Basic", "#tags column:3", "Front\tBack\tTags"]
        rows = [row + "\titembank" for row in rows]
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(header + rows) + "\n")
    print("%d items -> %s" % (len(qs), a.out))
    return 0
