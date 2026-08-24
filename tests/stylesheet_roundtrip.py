#!/usr/bin/env python3
"""Stylesheet invariants over every CSS this project emits -- the assertions
that would have caught two silent reader defects without a browser.

Nothing in the suite asserted over emitted CSS before this file, which is why
both defects shipped:

  D1 -- a stray `}` in `surfaces/lesson.py` closed `@media print{` one rule
        early, leaking seven print rules into the screen stylesheet. The
        leaked `[popover]{display:none}` is an author rule and outranks the
        UA `[popover]:not(:popover-open){display:none}`, so the glossary
        panel never rendered even when open, the reader section nav and the
        back-to-text links were invisible on screen, and callout shadows
        were flattened.
  D3 -- the four vendored `@font-face` urls were relative, so on a nested
        route such as `/lesson/<stem>` they resolved to `/lesson/fonts/...`,
        and the daemon carried no font route at all. Four 404s per page
        load.

Nine invariants, run over the union of two collectors so a stylesheet built
by a function is covered as well as one held in a constant:

  1. balanced braces in every collected stylesheet;
  2. no author rule outside an `@media print` block suppresses `[popover]`;
  3. every custom property a served document REFERENCES through `var(...)` is
     DEFINED somewhere in that same document (14-UI-SPEC §15 gate 8);
  4. every semantic colour token meets its contrast floor, measured with
     `surfaces.theme.contrast_ratio` itself (14-UI-SPEC §3.3, §3.4);
  5. every `@font-face` url is root-absolute, is a key of the daemon's closed
     font asset map, and the bytes behind it are readable;
  6. against a live daemon, each font url serves 200 `font/woff2`, and the
     same file name under a page-route prefix is a 404;
  7. EVERY served page -- reader and quiz alike -- declares all four
     manifest-recorded faces (14-UI-SPEC §15 gate 9);
  8. the daemon's font asset map names exactly the files fonts/MANIFEST.json
     records;
  9. inside the files this phase owns, no `font-size` outside
     {12,16,18,20,32}px, no `font-weight` outside {400,600}, and no literal
     font family (14-UI-SPEC §15 gate 12). Its scope is an explicit tuple and
     the files still owed are printed on every green run, so the debt is
     visible rather than pooled away.

Invariant 3 is the one that would have caught DEFECT D-A (`--space-1` …
`--space-7` referenced 64 times in `surfaces/lesson.py` and defined nowhere),
DEFECT D-B (`surfaces/quiz_page.py` carrying neither the shared token layer
nor an `@font-face` rule) and the `--panel` stray in `RUNNABLE_CSS`, none of
which any browser reports: an undefined custom property is not a parse error,
it silently resolves to the property's initial value.

Invariant 7 exists because invariants 5 and 6 POOL every collected stylesheet,
so a page that declares no `@font-face` at all passes them silently on the
strength of the pages that do. That pooling is exactly how D-B survived the
2026-08-12 font fix: the reader's four faces satisfied the pooled check while
the quiz, which had never joined the token layer, declared none.

Standard library only, no test framework, runnable as
`python tests/stylesheet_roundtrip.py`.
"""
import importlib, json, os, re, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import resources                                              # noqa: E402
import daemon_roundtrip                                       # noqa: E402
from surfaces import daemon                                   # noqa: E402

get = daemon_roundtrip.get
start_daemon = daemon_roundtrip.start_daemon

LESSON_BANK = os.path.join(ROOT, "fixtures", "lesson_bank.md")
PLAN = os.path.join(ROOT, "fixtures", "sample_plan.md")
MANIFEST = os.path.join(ROOT, "fonts", "MANIFEST.json")

STYLE_RE = re.compile(r"<style[^>]*>(.*?)</style>", re.S)
FONT_FACE_RE = re.compile(r"@font-face\s*\{([^{}]*)\}")
URL_RE = re.compile(r"url\(\s*[\"']?([^\"')]+)[\"']?\s*\)")
DISPLAY_NONE_RE = re.compile(r"display\s*:\s*none")
PRINT_AT_RE = re.compile(r"^@media\b.*\bprint\b", re.S)
CUSTOM_NAME_RE = re.compile(r"--[A-Za-z0-9_-]+")
CUSTOM_DEF_RE = re.compile(r"(?<![\w-])(--[A-Za-z0-9_-]+)\s*:")
SUPPORTS_PRELUDE_RE = re.compile(r"@supports[^{]*")

# The document every `collect_static()` entry belongs to. Module constants are
# fragments -- `LESSON_CSS` legitimately references a token the theme block
# supplies -- so they are pooled into one document that is REPORTED and never
# failed on. Only a served document, which is a whole rendered page, must be
# self-contained.
STATIC_DOC = "module constants (reported, never failed on)"

# The served documents gate 9 asserts, written out rather than derived from
# `collect_served`'s own route tuple: derived, a collector that stopped
# fetching the quiz would shrink the assertion instead of failing it, which is
# the shape of the pooling that let D-B through. `served /quiz/lesson_bank` is
# the route the shared-CSS include exists for.
REQUIRED_FONT_ROUTES = ("served /lesson/lesson_bank", "served /quiz/lesson_bank",
                        "served /study/lesson_bank", "served /day/sample_plan")

# `served /day/sample_plan` WAS the one recorded gap here. Plan 14-01 left it
# out because `surfaces/day.py` assembled its own document from
# `theme_css(cfg) + DAY_CSS` instead of going through
# `presentation.surface_shell`, so it carried neither the shared token layer
# nor a single face: the same defect as D-B, on a surface that phase did not
# own. Plan 17A-02 claimed the surface and migrated it, so the route moved up
# into the required set above and the reported set is now empty. Leaving the
# tuple in place, rather than deleting it, keeps the mechanism that made the
# gap visible for the next surface that needs it.
REPORTED_FONT_ROUTES = ()

# 14-UI-SPEC §15 gate 12. The project type scale is five sizes at two weights,
# and a family is named only by token (.planning/UI-SPEC.md §7).
TYPE_SCALE_SIZES = (12, 16, 18, 20, 32)
TYPE_SCALE_WEIGHTS = (400, 600)

# The scope is an EXPLICIT tuple rather than "every collected stylesheet",
# because the design contract records the rest of the migration as owed rather
# than as done, and a fixture that failed on the owed part would be red for a
# reason no plan in this phase is allowed to fix. A stylesheet is in scope when
# its collected name starts with one of these.
TYPE_SCALE_SCOPE = ("surfaces.presentation", "surfaces.lesson",
                    "served /lesson/", "surfaces.quiz_page",
                    "served /quiz/")

# 14-UI-SPEC section 3.4. These are the quiz response controls whose visible
# boundary identifies the component, so each must use the measured --edge
# token rather than the decorative --line token.
QUIZ_EDGE_CONTROLS = (".choice", ".opt", ".seg button", "button.ghost",
                      "textarea.ans", ".codewrap")
COLOUR_LITERAL_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgb|hsl)a?\s*\(")

# 14-UI-SPEC §17 item 6 -- the Phase 4 cleanup this phase deliberately does not
# widen its diff to reach. These files still carry off-scale sizes; the debt is
# printed on every green run so it stays visible instead of being forgotten.
# Plan 14-04 appends `surfaces.quiz_page` and `served /quiz/` to
# TYPE_SCALE_SCOPE once the quiz has been migrated; adding either early turns
# this fixture red for the wrong reason.
TYPE_SCALE_DEBT = ("surfaces.theme SETTINGS_CSS", "surfaces.day",
                   "surfaces.study")

# A length anywhere in a `font` shorthand. `font:inherit` carries none and is
# skipped; a shorthand that carries one must express it in px on the scale.
LENGTH_RE = re.compile(r"^\d*\.?\d+(px|em|rem|%|pt|ex|ch|vh|vw)\b")
VAR_ONLY_RE = re.compile(r"^var\(\s*--[A-Za-z0-9_-]+\s*\)$")

# 14-UI-SPEC §3.3/§3.4. Foregrounds are measured against three backgrounds
# each; a `*_bg` token is a BACKGROUND and is never itself a foreground -- a
# check that measures `warn_bg` against `bg` gets 1.03 and asserts the wrong
# thing.
SEMANTIC_FOREGROUNDS = ("warn", "unknown", "pending")
SEMANTIC_TEXT_FLOOR = 4.5
EDGE_BACKGROUNDS = ("card", "bg", "chip")
EDGE_FLOOR = 3.0


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


# ---- collection -------------------------------------------------------------

def surface_modules():
    """Every module under surfaces/ (plus surfaces.theme, which lives there),
    imported once. A module that cannot import is a failure, not a skip: a
    stylesheet nobody can load is a stylesheet nobody is checking."""
    mods = []
    for name in sorted(os.listdir(os.path.join(ROOT, "surfaces"))):
        if not name.endswith(".py") or name == "__init__.py":
            continue
        dotted = "surfaces." + name[:-3]
        try:
            mods.append(importlib.import_module(dotted))
        except Exception as exc:                    # noqa: BLE001
            fail("cannot import %s for the stylesheet scan: %s" % (dotted, exc))
    return mods


def collect_static():
    """Collector A: every module-level `*_CSS` string, plus the text of every
    `<style>` element inside every module-level string in the same modules.
    The second half is what catches `quiz_page.TEMPLATE`'s inline block,
    which no named constant holds."""
    sheets = []
    for mod in surface_modules():
        for key, value in sorted(vars(mod).items()):
            if not isinstance(value, str):
                continue
            if key.endswith("_CSS") and not key.endswith("_JS"):
                sheets.append(("%s.%s" % (mod.__name__, key), value))
            for n, block in enumerate(STYLE_RE.findall(value)):
                sheets.append(("%s.%s <style#%d>" % (mod.__name__, key, n),
                               block))
    return sheets


def collect_served(base):
    """Collector B: the text of every `<style>` element on each served page.
    This is what catches the glossary CSS `surfaces/lesson.py` builds in
    `_gloss_anchor_css` and `_gloss_print_css`, which no constant holds."""
    sheets = []
    for route in ("lesson/lesson_bank", "quiz/lesson_bank",
                  "study/lesson_bank", "day/sample_plan"):
        status, body = get(base + route)
        if status != 200:
            fail("served page /%s returned HTTP %s; the collector needs it"
                 % (route, status))
        blocks = STYLE_RE.findall(body)
        if not blocks:
            fail("served page /%s carries no <style> element" % route)
        for n, block in enumerate(blocks):
            sheets.append(("served /%s <style#%d>" % (route, n), block))
    return sheets


def normalise(css):
    """Blank out CSS comments and quoted-string contents, preserving length
    and newlines so an offset into the result names the same character in the
    raw text. A brace inside a comment or inside a url string can then never
    change a count or a depth."""
    out = list(css)
    i, n = 0, len(css)
    while i < n:
        ch = css[i]
        if ch == "/" and i + 1 < n and css[i + 1] == "*":
            end = css.find("*/", i + 2)
            end = n if end < 0 else end + 2
            for k in range(i, end):
                if out[k] != "\n":
                    out[k] = " "
            i = end
            continue
        if ch in "\"'":
            quote, j = ch, i + 1
            while j < n:
                if css[j] == "\\":
                    j += 2
                    continue
                if css[j] == quote:
                    j += 1
                    break
                j += 1
            for k in range(i, min(j, n)):
                if out[k] != "\n":
                    out[k] = " "
            i = min(j, n)
            continue
        i += 1
    return "".join(out)


def nearest_selector(raw, offset):
    """The nearest preceding non-empty line, so a brace-balance failure names
    something a human can find rather than the end of the file."""
    head = raw[:offset].rstrip()
    for line in reversed(head.splitlines()):
        if line.strip():
            return line.strip()
    return "(start of stylesheet)"


def blocks(norm):
    """Every brace block as {prelude, body, ancestors}, where `ancestors` is
    the tuple of enclosing preludes -- the at-block context invariant 2 needs
    in order to know which block a rule sits in."""
    found, stack, last = [], [], 0
    for i, ch in enumerate(norm):
        if ch == "{":
            stack.append((norm[last:i].strip(), i + 1))
            last = i + 1
        elif ch == "}":
            if not stack:
                last = i + 1
                continue
            prelude, start = stack.pop()
            found.append({"prelude": prelude, "body": norm[start:i],
                          "ancestors": tuple(p for p, _ in stack)})
            last = i + 1
    return found


# ---- invariant 1: balanced braces -------------------------------------------

def check_balanced_braces(sheets):
    for name, raw in sheets:
        norm = normalise(raw)
        depth = 0
        for i, ch in enumerate(norm):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth < 0:
                    fail("%s: unbalanced `}` at offset %d closes a block that "
                         "was never opened; nearest preceding selector is %r"
                         % (name, i, nearest_selector(raw, i)))
        if depth != 0:
            fail("%s: stylesheet ends at brace depth %d, expected 0; nearest "
                 "preceding selector is %r"
                 % (name, depth, nearest_selector(raw, len(raw))))


# ---- invariant 2: the popover panel is never suppressed on screen -----------

def check_popover_scope(sheets):
    """A `[popover]` rule that declares display:none is correct inside an
    `@media print` block and wrong anywhere else -- so this walks the block
    tree rather than searching the sheet, because the same declaration is
    both."""
    for name, raw in sheets:
        for rule in blocks(normalise(raw)):
            prelude = rule["prelude"]
            if prelude.startswith("@") or "[popover]" not in prelude:
                continue
            if not DISPLAY_NONE_RE.search(rule["body"]):
                continue
            if any(PRINT_AT_RE.match(a) for a in rule["ancestors"]):
                continue
            fail("%s: the author rule %r suppresses the popover panel outside "
                 "an @media print block, which outranks the UA "
                 "[popover]:not(:popover-open) rule and hides the glossary "
                 "even when it is open (enclosing at-blocks: %r)"
                 % (name, prelude, rule["ancestors"]))


# ---- invariant 3: every referenced custom property is defined ---------------

def document_key(name):
    """The rendered document a collected stylesheet belongs to.

    A served page carries several `<style>` elements and a token defined in
    one is available to all of them, so completeness is a per-DOCUMENT
    property, never a per-stylesheet one. `collect_served()` names its entries
    `served /<route> <style#N>`, so the route prefix is the document; every
    `collect_static()` entry pools into one reported-only document.
    """
    if name.startswith("served /"):
        return name.split(" <style#")[0]
    return STATIC_DOC


def var_references(norm):
    """`(name, offset)` for every custom property referenced as the FIRST
    argument of a `var(...)` call in normalised CSS.

    A declared fallback is not a reference: `var(--a, var(--b))` references
    `--a` only, because `--b` is what the author already knows to use when
    `--a` is absent. The scan therefore skips the whole call once a top-level
    comma is seen, nested `var()` calls included.
    """
    out, i, n = [], 0, len(norm)
    while True:
        start = norm.find("var(", i)
        if start < 0:
            return out
        k = start + 4
        while k < n and norm[k].isspace():
            k += 1
        m = CUSTOM_NAME_RE.match(norm, k)
        if m is None:
            i = start + 4
            continue
        depth, p, comma = 1, m.end(), -1
        while p < n:
            ch = norm[p]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    break
            elif ch == "," and depth == 1 and comma < 0:
                comma = p
            p += 1
        out.append((m.group(0), start))
        i = p + 1 if comma >= 0 else m.end()


def check_token_completeness(sheets):
    """14-UI-SPEC §15 gate 8. Every `var(--NAME)` a served document uses must
    resolve to a `--NAME:` declaration in that same document.

    An undefined custom property is invisible: no parse error, no console
    warning, the declaration simply resolves to the property's initial value.
    That is how 64 `--space-*` declarations in the reader shipped with no
    spacing at all.
    """
    docs = {}
    for name, raw in sheets:
        entry = docs.setdefault(document_key(name),
                                {"defined": set(), "refs": []})
        norm = normalise(raw)
        entry["defined"].update(m.group(1) for m in CUSTOM_DEF_RE.finditer(norm))
        skip = [m.span() for m in SUPPORTS_PRELUDE_RE.finditer(norm)]
        for prop, offset in var_references(norm):
            if any(lo <= offset < hi for lo, hi in skip):
                continue
            entry["refs"].append((prop, name, nearest_selector(raw, offset)))

    undefined = []
    for key in sorted(docs):
        entry, seen = docs[key], set()
        for prop, name, selector in entry["refs"]:
            if prop in entry["defined"] or prop in seen:
                continue
            seen.add(prop)
            undefined.append((key, prop, name, selector))

    reported = [row for row in undefined if row[0] == STATIC_DOC]
    if reported:
        print("note: %d custom propert%s referenced by a module constant is "
              "supplied by the served page rather than by the constant itself; "
              "reported, not failed on:" % (len(reported),
                                            "y" if len(reported) == 1 else "ies"))
        for _key, prop, name, selector in reported:
            print("  %s referenced in %s near %r" % (prop, name, selector))

    served = [row for row in undefined if row[0] != STATIC_DOC]
    if served:
        lines = ["%s: %s is referenced (in %s, near %r) and defined nowhere "
                 "in that document" % (key, prop, name, selector)
                 for key, prop, name, selector in served]
        fail("undefined custom properties reach a rendered page -- every one "
             "of these resolves to the property's initial value in a real "
             "browser, silently:\n  " + "\n  ".join(lines))


# ---- invariant 4: the semantic tokens meet their measured floors ------------

def check_semantic_token_contrast():
    """14-UI-SPEC §3.3 and §3.4, and the gate for requirement RTS-10.

    Measured with `surfaces.theme.contrast_ratio` itself -- never a second
    implementation and never a copied number -- so a hand-edited hex that
    drops below the floor fails the build rather than the learner's eyes.
    """
    from surfaces import theme                                  # noqa: PLC0415

    problems = []
    for mode in ("light", "dark"):
        semantic = theme.SEMANTIC_TOKENS.get(mode, {})
        base = theme.BASE_TOKENS.get(mode, {})
        for fg in SEMANTIC_FOREGROUNDS:
            paired = fg + "_bg"
            missing = [n for n in (fg, paired) if n not in semantic]
            if missing:
                problems.append("%s: SEMANTIC_TOKENS[%r] defines no %s"
                                % (mode, mode, " and no ".join(missing)))
                continue
            grounds = [("--%s (its own paired background)"
                        % paired.replace("_", "-"), semantic[paired])]
            for name in ("bg", "card"):
                if name in base:
                    grounds.append(("--%s" % name, base[name]))
            for label, value in grounds:
                ratio = theme.contrast_ratio(semantic[fg], value)
                if ratio < SEMANTIC_TEXT_FLOOR:
                    problems.append(
                        "%s: --%s %s on %s %s measures %.2f:1, below the %.1f:1 "
                        "text floor" % (mode, fg, semantic[fg], label, value,
                                        ratio, SEMANTIC_TEXT_FLOOR))
        if "edge" not in semantic:
            problems.append("%s: SEMANTIC_TOKENS[%r] defines no edge, so every "
                            "interactive control is still identified by --line "
                            "at 1.3:1" % (mode, mode))
            continue
        for name in EDGE_BACKGROUNDS:
            if name not in base:
                continue
            ratio = theme.contrast_ratio(semantic["edge"], base[name])
            if ratio < EDGE_FLOOR:
                problems.append(
                    "%s: --edge %s on --%s %s measures %.2f:1, below the %.1f:1 "
                    "non-text floor WCAG 1.4.11 requires of a boundary that "
                    "identifies a control" % (mode, semantic["edge"], name,
                                              base[name], ratio, EDGE_FLOOR))
    if problems:
        fail("semantic tokens do not meet their measured contrast floors:\n  "
             + "\n  ".join(problems))


# ---- invariant 9: the type scale is the only type scale ---------------------

def raw_blocks(raw):
    """Every brace block as {prelude, body, ancestors}, where `body` is the
    RAW text rather than the normalised text.

    `blocks()` returns normalised bodies, and `normalise()` blanks the contents
    of quoted strings -- which is exactly where a literal font family hides
    (`font-family:"Helvetica"`). Structure is still taken from the normalised
    text so a brace inside a comment or a url can never change the depth;
    `normalise()` preserves length, so an offset means the same character in
    both.
    """
    norm = normalise(raw)
    found, stack, last = [], [], 0
    for i, ch in enumerate(norm):
        if ch == "{":
            stack.append((norm[last:i].strip(), i + 1))
            last = i + 1
        elif ch == "}":
            if not stack:
                last = i + 1
                continue
            prelude, start = stack.pop()
            found.append({"prelude": prelude, "body": raw[start:i],
                          "norm": norm[start:i],
                          "ancestors": tuple(p for p, _ in stack)})
            last = i + 1
    return found


def declarations(rule):
    """`(property, value)` for every declaration directly in one rule body.

    Split at the semicolons of the NORMALISED body, so a `;` inside a comment
    or a quoted string never splits a declaration, then sliced out of the raw
    body so quoted values survive. A chunk carrying a brace belongs to a nested
    rule, which the walker visits on its own, and is skipped here.

    A declaration is a property followed by `:`. That is deliberate and load
    bearing: an SVG presentation attribute is written `font-size="14"` in
    markup and is NOT CSS -- the visual-item renderers legitimately set
    unitless `font-size` on `<text>` elements, and this invariant does not and
    must not govern them.
    """
    raw, norm = rule["body"], rule["norm"]
    cuts, start = [], 0
    for i, ch in enumerate(norm):
        if ch == ";":
            cuts.append(raw[start:i])
            start = i + 1
    cuts.append(raw[start:])
    out = []
    for chunk in cuts:
        if "{" in chunk or "}" in chunk:
            continue
        m = re.match(r"\s*([-A-Za-z][-A-Za-z0-9]*)\s*:\s*(.*)\s*$", chunk,
                     re.S)
        if m:
            out.append((m.group(1).lower(), m.group(2).strip()))
    return out


def bad_family_names(value):
    """The comma-separated family names in `value` that are not `var(--NAME)`."""
    return [part.strip() for part in value.split(",")
            if part.strip() and not VAR_ONLY_RE.match(part.strip())]


# ---- invariant 10: the 17A frozen token layer ------------------------------

# 17A-UI-SPEC Typography, frozen by plan 17A-02. Name to exact declared value.
# The set of VALUES is asserted to equal TYPE_SCALE_SIZES, so a sixth size
# cannot enter through a token while gate 12 keeps passing on literals.
FROZEN_TYPE_TOKENS = {"--text-xs": "12px", "--text-body": "16px",
                      "--text-lesson": "18px", "--text-heading": "20px",
                      "--text-display": "32px"}

# 17A-UI-SPEC Density tokens. Each row is (comfortable, compact), and each side
# must be an ALIAS of the existing spacing scale, never a raw length: that
# aliasing is the whole bound. --space-1 is the floor of the scale, so nothing
# tighter than 4px is expressible.
DENSITY_TOKENS = {"--density-row-gap": ("--space-3", "--space-2"),
                  "--density-card-pad": ("--space-3", "--space-2"),
                  "--density-list-gap": ("--space-2", "--space-1")}
# Matched against the RAW stylesheet, not the normalised one: `normalise`
# blanks quoted-string contents, so the word `compact` inside the attribute
# selector is whitespace by the time the brace scanner sees it.
COMPACT_SELECTOR_RE = re.compile(r"\[data-density\s*=\s*[\"']?compact")
DECL_RE = re.compile(r"(?<![\w-])(--[A-Za-z0-9_-]+)\s*:\s*([^;{}]+)")
TOUCH_TARGET_PX = 44


def declared_values(css, name):
    """Every value declared for one custom property in one stylesheet."""
    return [value.strip() for prop, value in DECL_RE.findall(normalise(css))
            if prop == name]


def check_frozen_type_tokens(sheets):
    """The five named type tokens exist, carry their UI-SPEC values, and add no
    sixth size to the scale gate 12 already polices.

    Gate 12 checks literal `font-size` declarations. Without this, a token
    could introduce a 14px sixth step and gate 12 would never see it, because
    the rule that consumes it reads `font-size:var(--text-small)`.
    """
    found = {}
    for name, raw in sheets:
        for token, expected in FROZEN_TYPE_TOKENS.items():
            for value in declared_values(raw, token):
                found.setdefault(token, set()).add(value)
                if value != expected:
                    fail("%s declares %s:%s; 17A-UI-SPEC freezes it at %s, and "
                         "a redefinition is how a scale stops being one"
                         % (name, token, value, expected))
    missing = sorted(set(FROZEN_TYPE_TOKENS) - set(found))
    if missing:
        fail("the frozen type tokens are not defined anywhere in the emitted "
             "CSS: %s. The freeze is a claim about served bytes, not about a "
             "specification document" % ", ".join(missing))
    sizes = set(int(v[:-2]) for v in FROZEN_TYPE_TOKENS.values())
    if sizes != set(TYPE_SCALE_SIZES):
        fail("the five frozen type tokens cover %s but the project type scale "
             "is %s; a token and a literal may not disagree about how many "
             "sizes exist" % (sorted(sizes), sorted(TYPE_SCALE_SIZES)))


def check_density_bounds(sheets):
    """Density is bounded because both sides alias the spacing scale.

    A raw pixel value on either side would let a future edit express a
    half-step, and the 44px touch floor is asserted to be independent of
    density in the same pass: a target sized by a density token is a target
    that shrinks when a panel goes compact.
    """
    comfortable, compact = {}, {}
    for name, raw in sheets:
        # Everything before the compact selector is the comfortable default,
        # everything from it onward is the compact override. Splitting on the
        # selector is enough because the override is one flat block.
        hit = COMPACT_SELECTOR_RE.search(raw)
        halves = ((raw, comfortable),) if not hit else \
                 ((raw[:hit.start()], comfortable), (raw[hit.start():], compact))
        for half, bucket in halves:
            for token in DENSITY_TOKENS:
                for value in declared_values(half, token):
                    if not VAR_ONLY_RE.match(value):
                        fail("%s declares %s:%s, which is not an alias of the "
                             "spacing scale; density stays bounded only while "
                             "every value is a var(--space-N)"
                             % (name, token, value))
                    alias = CUSTOM_NAME_RE.search(value).group(0)
                    bucket.setdefault(token, set()).add(alias)
    for token, (want_comfortable, want_compact) in DENSITY_TOKENS.items():
        got_c = comfortable.get(token, set())
        got_x = compact.get(token, set())
        if got_c != {want_comfortable}:
            fail("comfortable %s resolves to %s; 17A-UI-SPEC sets it to %s"
                 % (token, sorted(got_c) or "nothing", want_comfortable))
        if got_x != {want_compact}:
            fail("compact %s resolves to %s; 17A-UI-SPEC sets it to %s"
                 % (token, sorted(got_x) or "nothing", want_compact))
    for name, raw in sheets:
        norm = normalise(raw)
        for prop in ("min-height", "min-width"):
            for match in re.finditer(prop + r"\s*:\s*([^;{}]+)", norm):
                value = match.group(1).strip()
                if "--density-" in value:
                    fail("%s sizes a %s from a density token (%s). The %dpx "
                         "touch target is fixed regardless of density"
                         % (name, prop, value, TOUCH_TARGET_PX))


def check_type_scale(sheets):
    """14-UI-SPEC §15 gate 12: inside the files this phase owns, no font size
    outside {12,16,18,20,32}px, no font weight outside {400,600}, and no
    literal font family.

    Three exclusions, each real:

      - `@font-face` DESCRIPTOR blocks. A `font-weight` there declares what a
        FILE IS, not what a rule USES -- the vendored Quattro Bold is a
        700-weight file and must stay declared as one -- and its `font-family`
        is the family being defined, which cannot be a token.
      - SVG presentation attributes, excluded by `declarations()` requiring a
        `:` (see its docstring).
      - custom-property definitions: `--font-chrome:` is a definition, not a
        use, and `--measure-prose:59ch` is not a font declaration at all.

    Every scope prefix must match at least one collected stylesheet. A scoped
    assertion that matches nothing is green for the same reason an unscoped
    one is -- it checked nothing -- and that is the exact shape of the pooling
    that let D-B survive a green suite.
    """
    problems, covered = [], {prefix: 0 for prefix in TYPE_SCALE_SCOPE}
    for name, raw in sheets:
        if not name.startswith(TYPE_SCALE_SCOPE):
            continue
        for prefix in TYPE_SCALE_SCOPE:
            if name.startswith(prefix):
                covered[prefix] += 1
        for rule in raw_blocks(raw):
            context = (rule["prelude"],) + rule["ancestors"]
            if any(c.startswith("@font-face") for c in context):
                continue
            where = "%s: %r" % (name, rule["prelude"] or "(no selector)")
            for prop, value in declarations(rule):
                if prop.startswith("--"):
                    continue
                if prop == "font-size":
                    problems += size_problems(where, prop, value)
                elif prop == "font-weight":
                    if value.strip() not in [str(w) for w in TYPE_SCALE_WEIGHTS]:
                        problems.append(
                            "%s declares font-weight:%s; the project pair is "
                            "%s" % (where, value,
                                    "/".join(str(w) for w in TYPE_SCALE_WEIGHTS)))
                elif prop == "font-family":
                    bad = bad_family_names(value)
                    if bad:
                        problems.append(
                            "%s names the font %s literally; every family "
                            "resolves through a var(--NAME) token"
                            % (where, ", ".join(repr(b) for b in bad)))
                elif prop == "font":
                    problems += shorthand_problems(where, value)
    empty = [prefix for prefix in TYPE_SCALE_SCOPE if not covered[prefix]]
    if empty:
        fail("no stylesheet was collected for %s, so gate 12 asserted nothing "
             "about it and would stay green however far the type drifted"
             % ", ".join(repr(p) for p in empty))
    if problems:
        fail("the type scale is not the only type scale in the files this "
             "phase owns -- each of these reads as a different product from "
             "the rules around it:\n  " + "\n  ".join(problems))


def size_problems(where, prop, value):
    """A single length, asserted for unit first and magnitude second."""
    val = value.strip()
    m = LENGTH_RE.match(val)
    if not m:
        return ["%s declares %s:%s, which is not a length this scale can "
                "check; sizes are absolute px on the scale" % (where, prop, val)]
    if m.group(1) != "px":
        return ["%s declares %s:%s -- a relative unit resolves off-scale "
                "against whichever parent it inherits" % (where, prop, val)]
    number = float(val[:-2])
    if number not in [float(s) for s in TYPE_SCALE_SIZES]:
        return ["%s declares %s:%s; the project scale is %s"
                % (where, prop, val,
                   "/".join("%d" % s for s in TYPE_SCALE_SIZES))]
    return []


def shorthand_problems(where, value):
    """The `font` shorthand, split into its optional weight, its length and
    its family list. `font:inherit` carries no length and no family and is
    skipped -- it is the correct way for a control to take the surrounding
    type rather than restate it."""
    tokens = value.strip().split()
    size_at = next((i for i, t in enumerate(tokens) if LENGTH_RE.match(t)), -1)
    if size_at < 0:
        return []
    out = []
    for lead in tokens[:size_at]:
        if lead.isdigit():
            out += ["%s declares font-weight %s inside a font shorthand; the "
                    "project pair is %s"
                    % (where, lead,
                       "/".join(str(w) for w in TYPE_SCALE_WEIGHTS))] \
                if lead not in [str(w) for w in TYPE_SCALE_WEIGHTS] else []
    out += size_problems(where, "font (size)", tokens[size_at].split("/")[0])
    family = " ".join(tokens[size_at + 1:]).strip()
    if family:
        bad = bad_family_names(family)
        if bad:
            out.append("%s names the font %s literally in a font shorthand; "
                       "every family resolves through a var(--NAME) token"
                       % (where, ", ".join(repr(b) for b in bad)))
    return out


# ---- invariant 5: every @font-face url resolves -----------------------------

def font_urls(sheets):
    urls = {}
    for name, raw in sheets:
        for body in FONT_FACE_RE.findall(raw):
            for url in URL_RE.findall(body):
                urls.setdefault(url, name)
    return urls


def font_route_table():
    """The daemon's font asset prefix and closed map, reported as a failure
    rather than an AttributeError when the route does not exist -- a missing
    route is the defect this invariant is for, not a broken test."""
    prefix = getattr(daemon, "FONT_ASSET_PREFIX", None)
    table = getattr(daemon, "FONT_ASSETS", None)
    if prefix is None or table is None:
        fail("surfaces/daemon.py carries no font asset route "
             "(FONT_ASSET_PREFIX/FONT_ASSETS); every @font-face url the "
             "reader emits 404s")
    return prefix, table


def check_font_urls_resolve(sheets):
    urls = font_urls(sheets)
    if not urls:
        fail("no @font-face url was collected; the vendored faces must be "
             "declared in the token layer")
    prefix, table = font_route_table()
    for url, name in sorted(urls.items()):
        if not url.startswith("/"):
            fail("%s: @font-face url %r is relative, so a nested page route "
                 "such as /lesson/<stem> resolves it against the route and "
                 "404s; it must be root-absolute" % (name, url))
        if not url.startswith(prefix):
            fail("%s: @font-face url %r does not sit under the font asset "
                 "prefix %r" % (name, url, prefix))
        key = url[len(prefix):]
        entry = table.get(key)
        if entry is None:
            fail("%s: @font-face url %r has no entry in the daemon's closed "
                 "FONT_ASSETS map (key %r); the CSS names a file no route can "
                 "serve" % (name, url, key))
        relpath, mime = entry
        if mime != "font/woff2":
            fail("FONT_ASSETS[%r] declares MIME %r, expected font/woff2"
                 % (key, mime))
        try:
            body = resources.read_bytes(relpath)
        except OSError as exc:
            fail("FONT_ASSETS[%r] points at %r which the one resource reader "
                 "cannot read: %s" % (key, relpath, exc))
        if not body:
            fail("FONT_ASSETS[%r] resolves to zero bytes at %r"
                 % (key, relpath))


# ---- invariant 6: the live daemon serves them, and only at the real path ----

def check_fonts_served(base, sheets):
    urls = sorted(font_urls(sheets))
    for url in urls:
        if not url.startswith("/"):
            fail("@font-face url %r is relative, so it cannot be requested "
                 "from a live daemon at all; on /lesson/<stem> the browser "
                 "asks for /lesson/%s and gets a 404" % (url, url))
    for url in urls:
        status, ctype = head_asset(base, url)
        if status != 200:
            fail("GET %s returned HTTP %s from a live daemon; the reader has "
                 "never rendered in its intended typefaces" % (url, status))
        if ctype.split(";")[0].strip() != "font/woff2":
            fail("GET %s served content-type %r, expected font/woff2"
                 % (url, ctype))
    # The same file name resolved relative to a nested page route -- exactly
    # what a relative url produced -- must be a plain 404, never silently
    # aliased back onto the real asset.
    for url in urls:
        for route in ("lesson", "quiz", "study"):
            nested = "/%s/%s" % (route, url.lstrip("/"))
            status, _ctype = head_asset(base, nested)
            if status != 404:
                fail("GET %s returned HTTP %s; a font requested under a page "
                     "route prefix must be a plain 404" % (nested, status))


def head_asset(base, path):
    """`(status, content-type)` for an absolute path against the running
    daemon, treating a 404 as a normal outcome rather than an exception."""
    import urllib.error, urllib.request
    url = base.rstrip("/") + path
    try:
        with urllib.request.urlopen(url, timeout=10) as res:
            return res.status, res.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers.get("Content-Type", "")


# ---- invariant 7: EVERY served page declares the faces, not just some ------

def manifest_faces():
    """`{(family, weight)}` exactly as fonts/MANIFEST.json records it.

    Read, never restated: the manifest is the one source for which faces ship,
    so a fifth face added there is asserted on every route without touching
    this file.
    """
    man = json.load(open(MANIFEST, encoding="utf-8"))
    faces = set()
    for family in man["families"].values():
        for row in family["files"]:
            faces.add((family["family"], int(row["weight"])))
    return faces


def declared_faces(raw):
    """`{(family, weight)}` declared by the `@font-face` rules in one raw
    stylesheet. Read from the RAW text, never the normalised text, because
    `normalise()` blanks quoted strings and a family name is quoted."""
    faces = set()
    for body in FONT_FACE_RE.findall(raw):
        fam = re.search(r"font-family:\s*(?:\"([^\"]+)\"|'([^']+)'|([^;}\n]+))",
                        body)
        weight = re.search(r"font-weight:\s*(\d+)", body)
        if not fam or not weight:
            continue
        name = next(g for g in fam.groups() if g is not None).strip()
        faces.add((name, int(weight.group(1))))
    return faces


def check_every_served_page_declares_fonts(sheets):
    """14-UI-SPEC §15 gate 9: EVERY daemon-served page -- reader AND quiz --
    declares all four vendored faces.

    `check_font_urls_resolve` and `check_fonts_served` pool every collected
    stylesheet, so a page declaring no `@font-face` at all passes them in
    silence. This groups by rendered document instead, and reports the ROUTE
    that is missing a face rather than a bare count.
    """
    expected = manifest_faces()
    documents = {}
    for name, raw in sheets:
        key = document_key(name)
        if key == STATIC_DOC:
            continue
        documents.setdefault(key, set()).update(declared_faces(raw))

    # Named explicitly, so a collector that quietly stops fetching the quiz
    # fails here by route name instead of shrinking the assertion to whatever
    # it happened to fetch. `served /quiz/lesson_bank` is the one D-B removed.
    for route in REQUIRED_FONT_ROUTES:
        if route not in documents:
            fail("no stylesheet was collected for %s, so gate 9 would silently "
                 "stop asserting that route; the served-page collector must "
                 "cover every one of %r" % (route, list(REQUIRED_FONT_ROUTES)))

    problems, reported = [], []
    for route in sorted(documents):
        got = documents[route]
        missing = sorted(expected - got)
        extra = sorted(got - expected)
        bucket = problems if route in REQUIRED_FONT_ROUTES else reported
        if missing:
            bucket.append(
                "%s declares %d of the %d faces fonts/MANIFEST.json records; "
                "missing %s -- that page renders in the fallback stack and "
                "reads as a different product from the ones that do"
                % (route, len(got & expected), len(expected),
                   ", ".join("%s %d" % f for f in missing)))
        if extra:
            bucket.append(
                "%s declares %s, which fonts/MANIFEST.json does not record; "
                "the manifest is the one source for which faces ship"
                % (route, ", ".join("%s %d" % f for f in extra)))
    if reported:
        print("note: gate 9 is not yet asserted on every served route; these "
              "are reported on every run so the gap stays visible, and are "
              "not failed on because no plan owns their surface yet:")
        for line in reported:
            print("  " + line)
    if problems:
        fail("not every served page declares the vendored faces:\n  "
             + "\n  ".join(problems))


def check_no_colour_literal(sheets):
    """The in-scope surface rules consume theme tokens, never a second palette.

    surfaces.theme is deliberately excluded by TYPE_SCALE_SCOPE because it is
    the one palette source. Font-face descriptors are also excluded: embedded
    asset metadata is not a surface colour declaration.
    """
    problems = []
    for name, raw in sheets:
        if not name.startswith(TYPE_SCALE_SCOPE):
            continue
        for rule in raw_blocks(raw):
            context = (rule["prelude"],) + rule["ancestors"]
            if any(c.startswith("@font-face") for c in context):
                continue
            for prop, value in declarations(rule):
                # Served documents embed surfaces.theme's palette as custom
                # property definitions before the surface rules consume it.
                if prop.startswith("--"):
                    continue
                if COLOUR_LITERAL_RE.search(value):
                    problems.append("%s: %r declares %s:%s"
                                    % (name, rule["prelude"], prop, value))
    if problems:
        fail("surface stylesheets contain colour literals outside the sole "
             "palette in surfaces.theme:\n  " + "\n  ".join(problems))


def check_control_boundary_token(sheets):
    """Every quiz response control resolves its identifying border via --edge."""
    quiz_sheets = [(name, raw) for name, raw in sheets
                   if name.startswith(("surfaces.quiz_page", "served /quiz/"))]
    if not quiz_sheets:
        fail("no quiz stylesheet was collected for the control-boundary gate")
    problems = []
    for name, raw in quiz_sheets:
        rules = raw_blocks(raw)
        for selector in QUIZ_EDGE_CONTROLS:
            matches = [rule for rule in rules
                       if selector in [part.strip()
                                       for part in rule["prelude"].split(",")]]
            borders = [value for rule in matches
                       for prop, value in declarations(rule)
                       if prop == "border"]
            if not borders:
                problems.append("%s: %s has no border declaration"
                                % (name, selector))
            elif any("var(--edge)" not in value for value in borders):
                problems.append("%s: %s uses %s instead of var(--edge)"
                                % (name, selector, ", ".join(borders)))
    if problems:
        fail("quiz controls do not all use the 3:1 boundary token:\n  "
             + "\n  ".join(problems))


def check_svg_attributes_stay_out_of_type_scale():
    """Prove the quiz still has SVG text attributes the CSS parser ignores."""
    from surfaces import quiz_page
    source_strings = [value for value in vars(quiz_page).values()
                      if isinstance(value, str)]
    if not any("<text " in value and "font-size=\"" in value
               for value in source_strings):
        fail("quiz visual renderers no longer expose the SVG font-size control "
             "that proves the CSS type-scale matcher is declaration-only")


# ---- invariant 8: the map, the manifest and the CSS cannot drift ------------

def check_manifest_agreement():
    man = json.load(open(MANIFEST, encoding="utf-8"))
    recorded = set()
    for key, family in man["families"].items():
        for row in family["files"]:
            recorded.add("%s/%s" % (key, row["name"]))
    _prefix, table = font_route_table()
    served = set(table)
    if recorded != served:
        fail("the daemon's font asset map and fonts/MANIFEST.json name "
             "different files: only in the map %r, only in the manifest %r"
             % (sorted(served - recorded), sorted(recorded - served)))


def main():
    sheets = collect_static()
    workdir = tempfile.mkdtemp(prefix="stylesheet-")
    shutil.copy(LESSON_BANK, os.path.join(workdir, "lesson_bank.md"))
    shutil.copy(PLAN, os.path.join(workdir, "sample_plan.md"))
    proc, base, _lines = start_daemon(workdir)
    try:
        sheets += collect_served(base)
        check_balanced_braces(sheets)
        check_popover_scope(sheets)
        check_token_completeness(sheets)
        check_frozen_type_tokens(sheets)
        check_density_bounds(sheets)
        check_type_scale(sheets)
        check_no_colour_literal(sheets)
        check_control_boundary_token(sheets)
        check_svg_attributes_stay_out_of_type_scale()
        check_semantic_token_contrast()
        check_font_urls_resolve(sheets)
        check_fonts_served(base, sheets)
        check_every_served_page_declares_fonts(sheets)
        check_manifest_agreement()
    finally:
        proc.terminate()
        shutil.rmtree(workdir, ignore_errors=True)
    print("note: the type scale is asserted over %s only. Still off-scale, and "
          "owed rather than done (14-UI-SPEC section 17 item 6): %s. The quiz "
          "is now included in that scope."
          % (", ".join(TYPE_SCALE_SCOPE), ", ".join(TYPE_SCALE_DEBT)))
    print("ok: stylesheet roundtrip -- %d stylesheets balanced, popover never "
          "suppressed on screen, every var(--NAME) a served page references "
          "defined in that same page, no in-scope colour literals, quiz "
          "controls on --edge, semantic tokens at 4.5:1 and --edge at "
          "3:1 in both modes measured by theme.contrast_ratio, %d @font-face "
          "urls root-absolute, served 200 font/woff2, 404 under a page route, "
          "all %d manifest-recorded faces declared by each of the %d served "
          "routes (the quiz included), and in step with fonts/MANIFEST.json"
          % (len(sheets), len(font_urls(sheets)), len(manifest_faces()),
             len(REQUIRED_FONT_ROUTES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
