"""Shared Markdown block syntax for parsing, linting, and client rendering."""
import re


FENCE_RE = re.compile(r"^(`{3,})\s*(.*?)\s*$")


CALLOUT_MARK_RE = re.compile(r"^>\s*\[!([A-Za-z][^\]]*)\]\s*(.*)$")


# Shared locked labels for callout parsing and rendering.
CALLOUT_KINDS = {
    "KEY": ("key", "Key point"),
    "EXAMPLE": ("example", "Example"),
    "NOTE": ("note", "Note"),
    "WARNING": ("warning", "Warning"),
    # Phase 16A, D-16A-1 option-a: added alongside the shipped four rather
    # than promoting the dict into a semantic-role registry, so this dict
    # stays the one source of truth for what a callout kind means. The
    # container and its degradation contract are unchanged, which is what the
    # shared parser contract promises.
    "PREREQUISITE": ("prerequisite", "Before this"),
    "MISCONCEPTION": ("misconception", "Common mistake"),
    "TIP": ("tip", "Expert tip"),
    "COUNTEREXAMPLE": ("counterexample", "Counterexample"),
    "EXCERPT": ("excerpt", "From the source"),
    "UNCERTAINTY": ("uncertainty", "Not settled"),
    "SUMMARY": ("summary", "In short"),
}


def callout_spec(raw):
    """Map one `[!KIND]` marker to its locked `(slug, label, check_id)`
    triple, or None.

    `CHECK:` (with or without an id) maps to the reserved slot; the id is
    kept so Phase 6.2's live band can resolve the check item -- the inert
    slot drops it exactly as 3.1 did (the anchor carries no key and no
    scoring path until the band activates it). Any other kind returns None
    so the block classifier falls through to the pre-change paragraph
    output byte-for-byte: an unknown kind never raises and never invents a
    container.
    """
    kind = raw.strip()
    if kind.startswith("CHECK:"):
        m = re.match(r"^CHECK:\s*(\S+)", kind)
        check_id = m.group(1) if m else ""
        return ("check", "Check", check_id)
    slug, label = CALLOUT_KINDS.get(kind, (None, None))
    if slug is None:
        return None
    return (slug, label, None)


def callout_required_of(raw):
    """Split one captured `[!...]` marker into its `(kind, required)` pair.

    A trailing `!` inside the brackets declares the semantic required
    (D-16A-3): `MISCONCEPTION!` is `("MISCONCEPTION", True)` and
    `MISCONCEPTION` is `("MISCONCEPTION", False)`. This runs BEFORE any
    registry lookup and never consults one, so an unregistered kind still
    reports its required flag -- which is the whole point, because an unknown
    REQUIRED semantic must be refused out loud rather than falling through
    the unknown-optional paragraph path and disappearing.

    `CALLOUT_MARK_RE` is not involved and is not changed: its group 1 already
    accepts a trailing exclamation mark, so a bank using none of them captures
    byte identically.

    `CHECK:` is resolved by `callout_spec` before this function is consulted,
    exactly as it is today. `[!CHECK: id!]` is therefore not a supported form
    and is treated as an unknown kind; a later reader should not add a branch
    for it.
    """
    kind = (raw or "").strip()
    if kind.endswith("!"):
        return kind[:-1], True
    return kind, False


def callout_kind_of(line):
    """The dispatch key of one `> [!...]` line: the literal string "KEY"
    for any [!KEY] variant (the plan 03.1-03 card), the locked `(slug,
    label)` pair for the generic kinds, or None for an unknown kind that
    must degrade to the pre-change paragraph output."""
    m = CALLOUT_MARK_RE.match(line)
    if m is None:
        return None
    kind = m.group(1)
    if kind == "KEY" or kind.startswith("KEY:"):
        return "KEY"
    return callout_spec(kind)


def callout_entered(line):
    """True when one line opens a block the callout branch handles.

    Defined once because two guards share it: the branch itself, and the
    paragraph-continuation break. If only the branch knew about unknown
    required semantics, a required block sitting directly under a paragraph
    would be swallowed into that paragraph and lost, which is the same
    silent drop the whole contract exists to refuse.

    A known kind enters, exactly as it did before Phase 16A. An unknown kind
    enters only when it is marked required with a trailing `!`; an unknown
    optional kind still returns False and still falls through to the
    pre-16A paragraph output byte for byte.
    """
    m = CALLOUT_MARK_RE.match(line)
    if m is None:
        return False
    if callout_kind_of(line) is not None:
        return True
    return callout_required_of(m.group(1))[1]


def split_cells(row):
    row = row.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]
    return [c.strip() for c in row.split("|")]


def is_separator_row(row):
    return all(re.match(r"^:?-+:?$", c) for c in split_cells(row))


def protect_fenced_code(text):
    """Lift every fenced block out of a section's text before any inline
    pass, replacing each with an opaque placeholder line that no inline
    pattern can match. Returns `(protected_text, tokens)` with the fence info and
    verbatim code bodies in order.

    This ordering is the whole design: a single interleaved pass would let
    an emphasis or link pattern reach inside a fenced block and silently
    mangle exactly the content Phase 9 depends on being verbatim, and the
    damage would be invisible until someone read the rendered code closely.
    An unterminated fence treats the rest of the section as the block's
    content -- the forgiving reading that keeps the document readable
    (T-3-04).
    """
    lines = text.split("\n")
    out, tokens = [], []
    i = 0
    while i < len(lines):
        m = FENCE_RE.match(lines[i])
        if m:
            fence = m.group(1)
            info = m.group(2).strip()
            closer = re.compile(r"^`{%d,}\s*$" % len(fence))
            j = i + 1
            body = []
            while j < len(lines) and not closer.match(lines[j]):
                body.append(lines[j])
                j += 1
            if j < len(lines):
                j += 1  # skip the closing fence line
            tokens.append((info, "\n".join(body)))
            out.append("\x00K%d\x00" % (len(tokens) - 1))
            i = j
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out), tokens

