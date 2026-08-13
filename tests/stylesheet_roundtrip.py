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

Seven invariants, run over the union of two collectors so a stylesheet built
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
  7. the daemon's font asset map names exactly the files fonts/MANIFEST.json
     records.

Invariant 3 is the one that would have caught DEFECT D-A (`--space-1` …
`--space-7` referenced 64 times in `surfaces/lesson.py` and defined nowhere),
DEFECT D-B (`surfaces/quiz_page.py` carrying neither the shared token layer
nor an `@font-face` rule) and the `--panel` stray in `RUNNABLE_CSS`, none of
which any browser reports: an undefined custom property is not a parse error,
it silently resolves to the property's initial value.

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


# ---- invariant 7: the map, the manifest and the CSS cannot drift ------------

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
        check_semantic_token_contrast()
        check_font_urls_resolve(sheets)
        check_fonts_served(base, sheets)
        check_manifest_agreement()
    finally:
        proc.terminate()
        shutil.rmtree(workdir, ignore_errors=True)
    print("ok: stylesheet roundtrip -- %d stylesheets balanced, popover never "
          "suppressed on screen, every var(--…) a served page references "
          "defined in that same page, semantic tokens at 4.5:1 and --edge at "
          "3:1 in both modes measured by theme.contrast_ratio, %d @font-face "
          "urls root-absolute, served 200 font/woff2, 404 under a page route, "
          "and in step with fonts/MANIFEST.json"
          % (len(sheets), len(font_urls(sheets))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
