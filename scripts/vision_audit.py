#!/usr/bin/env python3
"""Check that user-vision entries actually reach the plan.

USER-VISION.md carries the goal in Weibao's words and an interpretation beside
each entry. The chain from an entry to a requirement to a phase is described in
that file but nothing verifies it, so an entry can sit there for weeks looking
answered while nothing downstream ever names it.

This reports five bounded structural checks:

  1. Every vision entry has a dated interpretation, or at minimum a dated
     pointer to where its interpretation already lives. A pointer is a weaker
     but honest state and is counted separately, never merged into the first.
  2. Every interpretation states a Planning effect.
  3. Recognized backtick paths resolve against explicit roots, with missing
     and ambiguous references reported separately.
  4. Entries have local inline links to their exact heading anchors elsewhere
     under .planning. Legacy prose remains unverified.
  5. Every interpretation names its relationship to earlier entries. This is
     the field that makes supersession inspectable, and it is the one most
     often left out, so it is counted separately and soft: a pointer-only
     entry is exempt.

It reports. It does not edit anything.
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

PLANNING = Path(".planning")
VISION = PLANNING / "USER-VISION.md"
INBOX = PLANNING / "USER-VISION-INBOX.md"
ENTRY = re.compile(r"^### (\d{4}-\d{2}-\d{2})[:— -]+\s*(.+)$")
PATHLIKE = re.compile(r"`([A-Za-z0-9_./-]+\.(?:md|py|json))`")
LINK = re.compile(r"\[[^\]\n]*\]\(([^\s)]+)\)")


def heading_anchor(text):
    """Support plain Markdown headings, with GitHub-style punctuation removal."""
    return re.sub(r"[^\w\- ]", "", text.lower()).replace(" ", "-")


def resolve_reference(rel, owner):
    """Resolve exact paths against the owner directory and repository root.

    Never search by basename. Two distinct matches are ambiguous, even when
    one would be a plausible legacy convention.
    """
    root = Path.cwd().resolve()
    hits = set()
    for base in (owner.parent, root):
        candidate = (base / rel).resolve()
        if candidate.is_relative_to(root) and candidate.is_file():
            hits.add(candidate)
    return sorted(hits)


def entries(path):
    if not path.exists():
        return []
    out, cur = [], None
    anchors = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        heading = re.match(r"^#{1,6} (.+)$", line)
        anchor = None
        if heading:
            base = heading_anchor(heading.group(1))
            count = anchors.get(base, 0)
            anchor = base if not count else f"{base}-{count}"
            anchors[base] = count + 1
        m = ENTRY.match(line)
        if m:
            cur = {"date": m.group(1), "title": m.group(2).strip(),
                   "anchor": anchor, "body": []}
            out.append(cur)
        elif cur is not None:
            cur["body"].append(line)
    for e in out:
        e["body"] = "\n".join(e["body"])
    return out


def planning_corpus():
    text, unreadable = [], []
    for p in PLANNING.rglob("*.md"):
        if p in {VISION, INBOX}:
            continue
        try:
            text.append((p, p.read_text(encoding="utf-8")))
        except (OSError, UnicodeError):
            unreadable.append(p)
            continue
    return text, unreadable


def main():
    if not VISION.exists():
        sys.exit("run this from the itembank repository root")

    ve = entries(VISION)
    ie = entries(INBOX)
    documents, unreadable = planning_corpus()
    corpus = "\n".join(text for _, text in documents)
    linked = set()
    unresolved_links = []
    anchors = {e["anchor"] for e in ve}
    for owner, text in documents:
        for target in LINK.findall(text):
            url = urlsplit(target)
            if url.scheme or url.netloc:
                continue
            path = unquote(url.path)
            if Path(path).name != VISION.name:
                continue
            hits = resolve_reference(path, owner)
            fragment = unquote(url.fragment)
            if hits == [VISION.resolve()] and fragment in anchors:
                linked.add(fragment)
            else:
                unresolved_links.append((owner, target))

    no_interp, no_effect, missing_paths, orphaned, pointer_only = [], [], [], [], []
    no_relationship = []
    ambiguous_paths, verified_paths, heuristic = [], [], []
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
            hits = resolve_reference(rel, VISION)
            if not hits:
                missing_paths.append((e, rel))
            elif len(hits) > 1:
                ambiguous_paths.append((e, rel))
            else:
                verified_paths.append((e, rel))
        if e["anchor"] not in linked:
            orphaned.append(e)
            if e["title"].lower() in corpus.lower():
                heuristic.append(e)

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
    show("Named files structurally resolved", verified_paths,
         lambda t: f"{t[0]['date']} names {t[1]}")
    show("Named files with ambiguous roots", ambiguous_paths,
         lambda t: f"{t[0]['date']} names {t[1]}")
    show("Interpretations naming no relationship to earlier entries",
         no_relationship, lambda e: f"{e['date']} {e['title'][:64]}")
    show("Entries nothing downstream mentions", orphaned,
         lambda e: f"{e['date']} {e['title'][:64]}")
    show("Entries with structurally verified downstream links",
         [e for e in ve if e['anchor'] in linked],
         lambda e: f"{e['date']} {e['title'][:64]}")
    show("Unverified title-text candidates", heuristic,
         lambda e: f"{e['date']} {e['title'][:64]}")
    show("Unresolved local vision links", unresolved_links,
         lambda row: f"{row[0]} names {row[1]}")
    show("Unindexed unreadable planning files", unreadable, str)
    show("Inbox entries with no disposition", undisposed,
         lambda e: f"{e['date']} {e['title'][:64]}")

    print("\nResolution roots: referencing file's directory and repository root.")
    print("Paths require exact files. Multiple matches are ambiguous.")
    print("The legacy downstream-mentions count now means no verified local")
    print("inline Markdown link to that exact vision heading anchor.")
    print("Dates and title prose never establish a link. Candidates stay unresolved.")
    print("Coverage: .planning Markdown files, backtick md/py/json paths, plain")
    print("heading anchors and inline local links only. Remote, reference-style")
    print("links, formatted headings and other legacy prose are unverified.")
    print("Structural links do not prove causal traceability or implementation.")
    print("Relationship counts remain a backlog. This read-only report exits zero.")


if __name__ == "__main__":
    main()
