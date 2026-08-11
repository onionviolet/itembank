#!/usr/bin/env python3
"""09-04 offline Math contract: the lesson reader renders inline and display
math from the vendored KaTeX distribution served by the daemon's closed
`/assets/katex/` map, with no CDN, no network fallback, no scorer/evidence
path, and readable failure states (D-06/D-07/D-08, 09-UI-SPEC Math).

What this proves end to end:
- A Math-profile lesson page references only local allowlisted assets, in
  order (CSS, core, auto-render), with display delimiters before inline and
  `trust:false`/`throwOnError:false`/`maxExpand:1000`/`maxSize:50`, and the
  adapter targets only `#lesson-content` and ignores `pre`/`code`.
- The daemon serves each known asset with the exact MIME and checkout bytes;
  unknown, encoded, traversal, and query-manipulated names are 404s and are
  never joined to a filesystem path.
- EMT/plain profiles render the pre-09-04 reader byte-for-byte (no math
  adapter), and a code fence containing `$` is never transformed.
- The packaged .pyz carries the same vendor bytes and serves them; the
  rendered page carries no http(s)/cdn reference.
- Fetching a lesson and its assets writes no evidence and changes no
  session/cursor state.

Standard library only, runnable as `python tests/math_offline_roundtrip.py`.
"""
import hashlib, json, os, re, shutil, subprocess, sys, tempfile, threading
import time, urllib.error, urllib.request, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import build                                                # noqa: E402
import model                                                 # noqa: E402
import resources                                            # noqa: E402
import subjects                                             # noqa: E402
import daemon_roundtrip                                      # noqa: E402
from surfaces import daemon, lesson                          # noqa: E402

get = daemon_roundtrip.get
json_request = daemon_roundtrip.json_request
start_daemon = daemon_roundtrip.start_daemon


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


# Fully invented Phase 9 math teaching content -- no real course material.
# Objectives are namespaced `math:` so subjects.select_profile resolves the
# math profile; the lesson carries inline `$...$`, display `$$...$$`, and a
# fence whose content is TeX/dollar shaped so the adapter must never touch
# it. Item types stay inside the math profile's allowlist.
MATH_BANK = """# Math intuition loop (synthetic, Phase 9)

Fully invented teaching content for the offline-math roundtrip. It is not
derived from any real course, exam, or textbook.

## LESSON

### The Power Rule

The power rule states that the derivative of $x^n$ is $n x^{n-1}$.

For a definite integral, the fundamental theorem gives:

$$\\int_a^b f(x)\\,dx = F(b) - F(a)$$

A malformed formula stays readable as source: $\\frac{1}{2

```python
price = 5  # $5 per unit, not math
```

### Limit Notation

The limit of $f(x)$ as $x$ approaches $c$ is written $\\lim_{x \\to c} f(x)$.

Q1. What is the derivative of $x^3$?   (difficulty: application)
[LESSON-REF: The Power Rule]
[OBJECTIVE: math:power-rule]

A) $3x^2$
B) $x^2$
C) $3x$
D) $\\frac{1}{4}x^4$

CORRECT: A

WHY BEST: The power rule multiplies by the exponent and subtracts one.

KEY DISCRIMINATOR: Apply the exponent as the coefficient.

DISTRACTOR ANALYSIS:
- A) Correct: bring the 3 down and lower the exponent to 2.
- B) This would be correct if the coefficient were dropped.
- C) This would be correct if the exponent were reduced by one without the coefficient.
- D) This would be correct for the antiderivative, not the derivative.

TRAP: Confusing the derivative with the antiderivative.

CONFIDENCE: high
"""


def write_math_workdir():
    workdir = tempfile.mkdtemp(prefix="math-offline-")
    with open(os.path.join(workdir, "math_bank.md"), "w",
              encoding="utf-8") as fh:
        fh.write(MATH_BANK)
    return workdir


def fetch_bytes(url, timeout=5):
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return res.status, res.headers.get("Content-Type", ""), res.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers.get("Content-Type", ""), exc.read()


def test_math_profile_page_emits_local_assets_in_order():
    """Test 1: a Math profile lesson emits local CSS/JS/auto-render
    references and ordered display-before-inline delimiters; the adapter is
    scoped to #lesson-content with safe options."""
    workdir = write_math_workdir()
    try:
        proc, url, lines = start_daemon(workdir)
        try:
            status, page = get(url + "lesson/math_bank")
            if status != 200:
                fail("math lesson GET returned %d" % status)
            for asset in ("/assets/katex/katex.min.css",
                          "/assets/katex/katex.min.js",
                          "/assets/katex/contrib/auto-render.min.js"):
                if asset not in page:
                    fail("math page is missing local asset reference %r" % asset)
            css_at = page.find("/assets/katex/katex.min.css")
            core_at = page.find("/assets/katex/katex.min.js")
            render_at = page.find("/assets/katex/contrib/auto-render.min.js")
            if not (0 <= css_at < core_at < render_at):
                fail("assets must load in order CSS, core, auto-render")
            if "renderMathInElement" not in page:
                fail("math page has no renderMathInElement adapter")
            if 'id="lesson-content"' not in page:
                fail("math page lacks the #lesson-content enhancement target")
            display_at = page.find('{left: "$$", right: "$$", display: true}')
            inline_at = page.find('{left: "$", right: "$", display: false}')
            if not (0 <= display_at < inline_at):
                fail("delimiters must order display before inline")
            for option in ("trust: false", "throwOnError: false",
                           "maxExpand: 1000", "maxSize: 50",
                           '"pre", "code"'):
                if option not in page:
                    fail("math adapter missing safe option %r" % option)
            # The raw source remains in the page (no server-side stripping).
            for src in ("$x^n$", "$$", "\\int_a^b"):
                if src not in page:
                    fail("math source %r was not preserved in the page" % src)
            # No network reference anywhere in the rendered page.
            for needle in ("https://", "http://", "cdn", "unpkg", "jsdelivr"):
                if needle in page:
                    fail("math page carries a network reference %r" % needle)
            # Adapter never calls the scorer, evidence, or session APIs.
            for forbidden in ("/api/submit", "/api/hint", "/api/report",
                              "score_response", "evidence", "fetch(",
                              "XMLHttpRequest"):
                if forbidden in page:
                    fail("math adapter reaches %r -- must be presentation "
                         "only (D-08)" % forbidden)
        finally:
            proc.terminate()
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def test_asset_route_exact_mime_and_checkout_bytes():
    """Test 2: each known asset resolves through the daemon with the exact
    MIME type and the exact checkout bytes from resources.read_bytes()."""
    workdir = write_math_workdir()
    try:
        proc, url, lines = start_daemon(workdir)
        try:
            base = url.rstrip("/")
            for name, mime in (
                    ("katex.min.css", "text/css; charset=utf-8"),
                    ("katex.min.js", "application/javascript; charset=utf-8"),
                    ("contrib/auto-render.min.js",
                     "application/javascript; charset=utf-8"),
                    ("fonts/KaTeX_Main-Regular.woff2", "font/woff2"),
                    ("fonts/KaTeX_Main-Regular.woff", "font/woff"),
                    ("fonts/KaTeX_Main-Regular.ttf", "font/ttf")):
                status, ctype, body = fetch_bytes(
                    "%s/assets/katex/%s" % (base, name))
                if status != 200:
                    fail("GET /assets/katex/%s returned %d" % (name, status))
                if not ctype.startswith(mime):
                    fail("asset %r MIME %r != %r" % (name, ctype, mime))
                expected = resources.read_bytes("vendor/katex/" + name)
                if body != expected:
                    fail("asset %r bytes differ from the checkout vendor "
                         "tree" % name)
            # Every font katex.min.css references is servable.
            css = resources.read_text("vendor/katex/katex.min.css")
            fonts = sorted(set(re.findall(r"url\(fonts/([^)]+)\)", css)))
            for font in fonts:
                status, ctype, _ = fetch_bytes(
                    "%s/assets/katex/fonts/%s" % (base, font))
                if status != 200:
                    fail("CSS-referenced font %r returned %d" % (font, status))
        finally:
            proc.terminate()
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def test_hostile_asset_names_are_404():
    """Test 3: unknown, encoded, nested, traversal, and query-manipulated
    names are 404s and never leak bytes or join a filesystem path."""
    workdir = write_math_workdir()
    try:
        proc, url, lines = start_daemon(workdir)
        try:
            base = url.rstrip("/")
            hostile = (
                "/assets/katex/unknown.js",
                "/assets/katex/..%2f..%2fmodel.py",
                "/assets/katex/%2e%2e%2fmodel.py",
                "/assets/katex/..%2f..%2f..%2fetc%2fpasswd",
                "/assets/katex/fonts/..%2f..%2fmodel.py",
                "/assets/katex/KaTeX_Main-Regular.woff2/extra",
                "/assets/katex/katex.min.css/../../model.py",
            )
            for path in hostile:
                status, ctype, body = fetch_bytes(base + path)
                if status != 404:
                    fail("hostile asset %r returned %d, expected 404"
                         % (path, status))
                if b"def parse_bank" in body or b"root:" in body:
                    fail("hostile asset %r leaked repository bytes" % path)
            # A query cannot change which resource is served: the path is
            # the whole address, the query is ignored (never joined to disk).
            status, _, body = fetch_bytes(
                base + "/assets/katex/katex.min.css?p=/model.py")
            if status != 200:
                fail("known asset with a query returned %d" % status)
            if body != resources.read_bytes("vendor/katex/katex.min.css"):
                fail("query-manipulated asset request changed the bytes")
        finally:
            proc.terminate()
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def test_emt_and_plain_profiles_emit_no_math_adapter():
    """Test 4: EMT/plain profiles stay ordinary shared-reader output -- no
    math assets, no adapter -- and a `$` inside a code fence is untouched."""
    workdir = tempfile.mkdtemp(prefix="math-offline-")
    try:
        shutil.copy(os.path.join(ROOT, "fixtures", "sample_bank.md"),
                    os.path.join(workdir, "sample_bank.md"))
        # The EMT fixture from tests/subject_loop_roundtrip.py (namespaced
        # emt objectives) plus the fence content that must survive.
        emt = open(os.path.join(ROOT, "tests", "subject_loop_roundtrip.py"),
                   encoding="utf-8").read()
        start = emt.find('EMT_BANK = """')
        if start < 0:
            fail("subject_loop_roundtrip.py has no EMT_BANK fixture")
        start += len('EMT_BANK = """')
        end = emt.find('"""', start)
        emt_bank = emt[start:end]
        with open(os.path.join(workdir, "emt_bank.md"), "w",
                  encoding="utf-8") as fh:
            fh.write(emt_bank)
        proc, url, lines = start_daemon(workdir)
        try:
            for stem in ("sample_bank", "emt_bank"):
                status, page = get(url + "lesson/" + stem)
                if status != 200:
                    fail("%s lesson GET returned %d" % (stem, status))
                if "/assets/katex/" in page or "renderMathInElement" in page:
                    fail("%s profile emitted the math adapter (D-08)"
                         % stem)
                if 'id="lesson-content"' not in page:
                    fail("%s page lost the shared #lesson-content target"
                         % stem)
            # The EMT fixture's dollar-shaped fence is untouched by math.
            if "$not math$" not in page:
                fail("EMT fence content was not preserved verbatim")
        finally:
            proc.terminate()
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def test_offline_page_writes_no_evidence_and_no_session_delta():
    """Test 5: fetching a math lesson and its assets writes no evidence and
    touches no session -- the enhancement is presentation only (D-08)."""
    workdir = write_math_workdir()
    try:
        proc, url, lines = start_daemon(workdir)
        try:
            base = url.rstrip("/")
            status, _ = get(base + "/lesson/math_bank")
            if status != 200:
                fail("math lesson GET returned %d" % status)
            fetch_bytes(base + "/assets/katex/katex.min.css")
            fetch_bytes(base + "/assets/katex/katex.min.js")
            fetch_bytes(base + "/assets/katex/contrib/auto-render.min.js")
            fetch_bytes(base + "/assets/katex/fonts/KaTeX_Main-Regular.woff2")
            evidence_dirs = []
            for dp, _, fns in os.walk(workdir):
                if "_evidence" in dp or any(f.endswith(".jsonl") for f in fns):
                    evidence_dirs.append(os.path.join(dp, *fns))
            if evidence_dirs:
                fail("math lesson fetch wrote evidence: %r" % evidence_dirs)
            # `_attempts/` exists because the daemon itself creates a
            # per-bank session bookkeeping dir at startup -- the lesson
            # fetch must add no session file to it.
            attempts = os.path.join(workdir, "_attempts")
            if os.path.isdir(attempts):
                leaked = [n for n in os.listdir(attempts)
                          if n.startswith("session_") or n.endswith(".json")]
                if leaked:
                    fail("math lesson fetch created session files: %r"
                         % leaked)
        finally:
            proc.terminate()
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def test_packaged_artifact_serves_the_same_assets():
    """Test 6: the .pyz carries the identical vendor bytes and a daemon
    running from the packaged artifact serves them from the archive."""
    workdir = write_math_workdir()
    out_dir = tempfile.mkdtemp(prefix="math-offline-pyz-")
    try:
        artifact = build.build(out_dir)
        with zipfile.ZipFile(artifact) as zf:
            names = set(n for n in zf.namelist() if not n.endswith("/"))
            for member in ("vendor/katex/katex.min.css",
                           "vendor/katex/katex.min.js",
                           "vendor/katex/contrib/auto-render.min.js",
                           "vendor/katex/LICENSE"):
                if member not in names:
                    fail("the .pyz is missing %r" % member)
                if zf.read(member) != resources.read_bytes(member):
                    fail("vendored member %r differs between checkout and "
                         ".pyz" % member)
        # A daemon launched from the artifact serves the archive's bytes.
        proc = subprocess.Popen(
            [sys.executable, artifact, "daemon", workdir, "--no-open",
             "--port", "0"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        lines = []
        threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                         daemon=True).start()
        url = None
        try:
            for _ in range(60):
                time.sleep(0.1)
                m = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
                if m:
                    url = m.group(0)
                    break
            if not url:
                fail("packaged daemon never printed a URL. Output was:\n"
                     + "".join(lines))
            base = url.rstrip("/")
            for name in ("katex.min.css", "katex.min.js",
                         "contrib/auto-render.min.js"):
                status, _, body = fetch_bytes(base + "/assets/katex/" + name)
                if status != 200:
                    fail("packaged daemon returned %d for %r" % (status, name))
                if body != resources.read_bytes("vendor/katex/" + name):
                    fail("packaged daemon served different bytes for %r"
                         % name)
        finally:
            proc.terminate()
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
        shutil.rmtree(out_dir, ignore_errors=True)


def test_profile_snapshot_drives_the_presentation_seam():
    """Test 7: lesson_page's profile seam -- math on only when the snapshot's
    lesson.math flag is true, byte-identical reader otherwise."""
    workdir = write_math_workdir()
    try:
        path = os.path.join(workdir, "math_bank.md")
        qs = model.load(path)
        registry = subjects.load_registry(workdir)
        math_snap = subjects.select_profile(qs, registry)  # math objectives
        plain_snap = {"registry_version": 1, "profile_version": 1,
                      "subject_id": "", "profile": subjects.DEFAULT_PROFILE,
                      "unsupported_capabilities": []}
        pg_math = lesson.lesson_page(path, qs, model.parse_lesson(path),
                                     profile=math_snap)
        pg_plain = lesson.lesson_page(path, qs, model.parse_lesson(path),
                                      profile=plain_snap)
        pg_none = lesson.lesson_page(path, qs, model.parse_lesson(path))
        if "/assets/katex/" not in pg_math or "renderMathInElement" not in pg_math:
            fail("math profile snapshot did not enable the adapter")
        if pg_plain != pg_none:
            fail("plain profile snapshot changed the reader byte-for-byte")
        if "/assets/katex/" in pg_none:
            fail("no profile emitted the math adapter")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def main():
    test_math_profile_page_emits_local_assets_in_order()
    test_asset_route_exact_mime_and_checkout_bytes()
    test_hostile_asset_names_are_404()
    test_emt_and_plain_profiles_emit_no_math_adapter()
    test_offline_page_writes_no_evidence_and_no_session_delta()
    test_packaged_artifact_serves_the_same_assets()
    test_profile_snapshot_drives_the_presentation_seam()
    print("math offline contract: ok (local-only asset graph, exact MIME/"
          "bytes, hostile 404s, profile gating, code-fence immunity, zero "
          "evidence/session delta, packaged parity, presentation seam)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
