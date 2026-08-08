"""Anki TSV export: Basic and Cloze, generic to any bank.

Subject-specific packaging (Mandarin TTS, `.apkg` building) stays out, because
it needs dependencies and network access that this tool refuses to grow.
"""
import os, re, sys

from model import lint, load
from runtime import answer_text
from surfaces import gift


def tsv_cell(value):
    return re.sub(r"\s+", " ", str(value or "")).replace("\t", " ").strip()


def cmd_export(a):
    if a.format == "gift":
        return gift.export_gift(a)
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
