#!/usr/bin/env python3
"""Check that user-vision entries actually reach the plan.

USER-VISION.md carries the goal in Weibao's words and an interpretation beside
each entry. The chain from an entry to a requirement to a phase is described in
that file but nothing verifies it, so an entry can sit there for weeks looking
answered while nothing downstream ever names it.

This checks four things, all mechanically:

  1. Every vision entry has a dated interpretation, or at minimum a dated
     pointer to where its interpretation already lives. A pointer is a weaker
     but honest state and is counted separately, never merged into the first.
  2. Every interpretation states a Planning effect.
  3. Every file path an interpretation names actually exists.
  4. Every entry is referenced somewhere else under .planning, or is flagged
     as orphaned.
  5. Every interpretation names its relationship to earlier entries. This is
     the field that makes supersession inspectable, and it is the one most
     often left out, so it is counted separately and soft: a pointer-only
     entry is exempt.

It reports. It does not edit anything.
"""
import re
import sys
from pathlib import Path

PLANNING = Path(".planning")
VISION = PLANNING / "USER-VISION.md"
INBOX = PLANNING / "USER-VISION-INBOX.md"
ENTRY = re.compile(r"^### (\d{4}-\d{2}-\d{2})[:— -]+\s*(.+)$")
PATHLIKE = re.compile(r"`([A-Za-z0-9_./-]+\.(?:md|py|json))`")


def entries(path):
    if not path.exists():
        return []
    out, cur = [], None
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = ENTRY.match(line)
        if m:
            cur = {"date": m.group(1), "title": m.group(2).strip(), "body": []}
            out.append(cur)
        elif cur is not None:
            cur["body"].append(line)
    for e in out:
        e["body"] = "\n".join(e["body"])
    return out


def planning_corpus():
    text = []
    for p in PLANNING.rglob("*.md"):
        if p.name in {"USER-VISION.md", "USER-VISION-INBOX.md"}:
            continue
        try:
            text.append(p.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
    return "\n".join(text)


def main():
    if not VISION.exists():
        sys.exit("run this from the itembank repository root")

    ve = entries(VISION)
    ie = entries(INBOX)
    corpus = planning_corpus()

    no_interp, no_effect, missing_paths, orphaned, pointer_only = [], [], [], [], []
    no_relationship = []
    # Both spellings are accepted on purpose: the record has used "prior" since
    # 2026-08-14 and the extracted skill says "earlier". Until one wins, a check
    # that knows only one of them would report a field that is actually there.
    REL = ("Relationship to prior entries", "Relationship to earlier entries")
    for e in ve:
        body = e["body"]
        has_interp = ("Interpretation recorded" in body
                      or "Interpretation update" in body)
        has_pointer = "Interpretation pointer recorded" in body
        if has_pointer and not has_interp:
            pointer_only.append(e)
        elif not has_interp:
            no_interp.append(e)
        if "Planning effect" not in body and not has_pointer:
            no_effect.append(e)
        if not has_pointer and not any(r in body for r in REL):
            no_relationship.append(e)
        for m in PATHLIKE.finditer(body):
            rel = m.group(1)
            if rel.startswith("<"):
                continue
            if rel.startswith("-"):
                # A suffix written as prose, e.g. "129 `-SUMMARY.md` files".
                # It names a shape, not a file, so it can never resolve.
                continue
            hits = list(Path(".").rglob(Path(rel).name))
            if not hits:
                missing_paths.append((e, rel))
        key = e["title"].split(",")[0].strip().lower()
        probe = key[:28]
        if probe and probe not in corpus.lower() and e["date"] not in corpus:
            orphaned.append(e)

    undisposed = [e for e in ie if "**Disposition:**" not in e["body"]
                  and "**Status:**" not in e["body"]]

    def show(title, rows, fmt):
        print(f"\n{title}: {len(rows)}")
        for r in rows[:12]:
            print("  " + fmt(r))
        if len(rows) > 12:
            print(f"  ... and {len(rows) - 12} more")

    print(f"USER-VISION entries: {len(ve)}    inbox entries: {len(ie)}")
    show("Entries carried by a pointer, not a full interpretation", pointer_only,
         lambda e: f"{e['date']} {e['title'][:64]}")
    show("Entries with no dated interpretation", no_interp,
         lambda e: f"{e['date']} {e['title'][:64]}")
    show("Entries stating no planning effect", no_effect,
         lambda e: f"{e['date']} {e['title'][:64]}")
    show("Named files that do not exist", missing_paths,
         lambda t: f"{t[0]['date']} names {t[1]}")
    show("Interpretations naming no relationship to earlier entries",
         no_relationship, lambda e: f"{e['date']} {e['title'][:64]}")
    show("Entries nothing downstream mentions", orphaned,
         lambda e: f"{e['date']} {e['title'][:64]}")
    show("Inbox entries with no disposition", undisposed,
         lambda e: f"{e['date']} {e['title'][:64]}")

    print("\nTwo soft checks. Orphaned matches on title text, so a real")
    print("reference worded differently reads as orphaned. The relationship")
    print("count is a backlog, not a failure: an entry that genuinely stands")
    print("alone has no earlier entry to relate to. The first three are exact.")


if __name__ == "__main__":
    main()
