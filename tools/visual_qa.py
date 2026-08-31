#!/usr/bin/env python3
"""Dev-only driven-browser QA harness for the 17A visual foundation (D-09).

jsdom does no layout, so the width, zoom, focus-visibility, target-size,
contrast, motion, and touch gates need a real layout engine. This harness
drives the pinned Playwright Chromium (VENDORED.md row `playwright`,
approved in 17A-04-DECISIONS.md D-17A-04-1) over the synthetic visual
fixture and reports measured evidence. It is a development tool: nothing in
the shipped runtime imports it, and when Playwright is absent it refuses
with one line rather than degrading into DOM-only claims.

What this harness is NOT: an accessibility certification. It produces
repeatable layout evidence for the scripted human review that owns A11Y-01
acceptance. An agent never self-certifies accessibility.

The matrix (17A-04 Task 1):
  widths 1280 / 768 / 375 with no horizontal overflow, 200 percent zoom
  reflow (viewport 640, the WCAG 1.4.4 equivalence), keyboard order with
  visible focus and no trap, 44px targets for non-inline controls, text
  contrast in light, dark, and oled, reduced motion honored, disclosure
  touch equivalence, the no-script static fallback, and one deliberately
  hover-only page that MUST fail the equivalence audit (REQUIREMENTS.md
  A11Y-01; synthesis 12.4 rejects hover-only equivalence).

Exit codes: 0 the matrix is as expected (every positive gate passes and the
negative fixture fails for the equivalence reason), 1 any unexpected
result, 3 Playwright is not installed (a refusal, not a failure).

Usage:
  python tools/visual_qa.py                 human-readable lines
  python tools/visual_qa.py --json PATH     also write the evidence JSON
  python tools/visual_qa.py --shots DIR     also write screenshots to DIR
"""
import argparse
import hashlib
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("refused: the pinned dev-only Playwright harness is not installed "
          "(see VENDORED.md row `playwright`); the QA matrix falls back to "
          "human review")
    sys.exit(3)

from surfaces import theme                                 # noqa: E402
from surfaces import visual_fixture                        # noqa: E402

WIDTHS = (1280, 768, 375)
ZOOM_WIDTH = 640          # 200 percent of the 1280 desktop layout.
MIN_TARGET = 44           # UI-SPEC section 8: touch targets >= 44px.
MIN_TEXT_CONTRAST = 4.5   # WCAG AA normal text.
MIN_LARGE_CONTRAST = 3.0  # WCAG AA large text.


# --------------------------------------------------------------------------
# The three pages under test. All synthetic, all built in a temp directory,
# nothing written into the repository.
# --------------------------------------------------------------------------

def build_pages(work):
    """fixture.html (light/dark via media query), oled.html, hover_only.html."""
    html = visual_fixture.single_file()
    fixture = os.path.join(work, "fixture.html")
    open(fixture, "w", encoding="utf-8").write(html)

    # The fixture emits the system theme (light root plus a dark media
    # override). oled is a forced mode, so the oled leg appends the oled
    # root block AFTER the existing theme CSS: same specificity, later
    # wins, and the tokens are exactly what `itembank config set theme
    # oled` would serve.
    oled_root = theme.theme_css({"theme": "oled",
                                 "accent": theme.DEFAULT_THEME_CONFIG["accent"]})
    oled_html = html.replace(
        "</head>", "<style>%s</style></head>" % oled_root, 1)
    oled = os.path.join(work, "oled.html")
    open(oled, "w", encoding="utf-8").write(oled_html)

    # The deliberately hover-only negative fixture: same tokens, one
    # definition revealed ONLY by :hover on a non-focusable span. This page
    # exists to prove the equivalence audit can fail; it must never pass.
    negative_html = (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<title>Hover-only negative fixture (synthetic)</title>"
        "<style>%s</style>"
        "<style>"
        "body{font-family:sans-serif;max-width:60ch;margin:2rem auto;"
        "color:var(--ink);background:var(--bg)}"
        ".term{border-bottom:1px dotted var(--accent);position:relative}"
        ".term .def{display:none;position:absolute;top:1.4em;left:0;"
        "background:var(--card);color:var(--ink);padding:8px;"
        "border:1px solid var(--line);width:24ch}"
        ".term:hover .def{display:block}"
        "</style></head><body>"
        "<h1>Synthetic negative page</h1>"
        "<p>The <span class=\"term\">osmotic gradient"
        "<span class=\"def\">An invented definition, reachable only by "
        "pointer hover. This page must fail equivalence review.</span>"
        "</span> drives the flow in this fictional system.</p>"
        "</body></html>"
        % theme.theme_css(theme.DEFAULT_THEME_CONFIG))
    negative = os.path.join(work, "hover_only.html")
    open(negative, "w", encoding="utf-8").write(negative_html)
    return fixture, oled, negative


def file_url(path):
    return "file://" + path


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


# --------------------------------------------------------------------------
# In-page measurement scripts. Everything measured comes back as JSON so the
# verdict is computed in Python where it can be asserted and recorded.
# --------------------------------------------------------------------------

JS_OVERFLOW = """() => {
  const doc = document.documentElement;
  return {scrollWidth: doc.scrollWidth, innerWidth: window.innerWidth,
          clientWidth: doc.clientWidth};
}"""

# Contrast: computed foreground against the first non-transparent ancestor
# background, over every visible element that directly contains text. The
# fixture uses solid token backgrounds, so ancestor-walking is exact here.
JS_CONTRAST = """() => {
  function parse(c) {
    const m = c.match(/rgba?\\(([^)]+)\\)/);
    if (!m) return null;
    const p = m[1].split(",").map(parseFloat);
    return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1};
  }
  function lum(c) {
    const f = v => { v /= 255;
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
  }
  function ratio(a, b) {
    const l1 = lum(a), l2 = lum(b);
    return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
  }
  function effBg(el) {
    let e = el;
    while (e) {
      const c = parse(getComputedStyle(e).backgroundColor);
      if (c && c.a > 0.99) return c;
      e = e.parentElement;
    }
    return {r: 255, g: 255, b: 255, a: 1};
  }
  const out = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const seen = new Set();
  let node;
  while ((node = walker.nextNode())) {
    if (!node.textContent.trim()) continue;
    const el = node.parentElement;
    if (!el || seen.has(el)) continue;
    seen.add(el);
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden") continue;
    const rect = el.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) continue;
    const fg = parse(cs.color);
    if (!fg) continue;
    const size = parseFloat(cs.fontSize);
    const bold = parseInt(cs.fontWeight, 10) >= 700;
    const large = size >= 24 || (bold && size >= 18.66);
    out.push({
      tag: el.tagName.toLowerCase(),
      cls: (el.className && el.className.baseVal !== undefined
            ? el.className.baseVal : el.className || "").toString().slice(0, 60),
      text: node.textContent.trim().slice(0, 40),
      size: size, large: large,
      ratio: Math.round(ratio(fg, effBg(el)) * 100) / 100,
    });
    if (out.length >= 400) break;
  }
  return out;
}"""

# Target size: every visible natively-interactive element. Inline targets
# (in a line of text) carry the WCAG 2.5.8 inline exemption and are
# reported, not failed. Hidden switch radios are measured through their
# labels, which are the real targets.
JS_TARGETS = """() => {
  const out = [];
  const els = document.querySelectorAll(
    "button, summary, a[href], input, select, textarea, label[for]");
  for (const el of els) {
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden") continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;
    if (el.tagName === "INPUT" && (r.width <= 1 || r.height <= 1)) continue;
    const parentDisplay = el.parentElement
      ? getComputedStyle(el.parentElement).display : "block";
    const inline = cs.display.startsWith("inline")
      && ["block", "flow-root", "list-item"].includes(parentDisplay) === false
      || (el.closest("p, li, dd, td") !== null);
    out.push({tag: el.tagName.toLowerCase(),
              cls: (el.className || "").toString().slice(0, 60),
              text: (el.textContent || "").trim().slice(0, 40),
              w: Math.round(r.width), h: Math.round(r.height),
              inline: !!inline});
  }
  return out;
}"""

JS_FOCUS_INFO = """() => {
  const el = document.activeElement;
  if (!el || el === document.body) return {tag: "body"};
  function visibleOutline(target) {
    const cs = getComputedStyle(target);
    return cs.outlineStyle !== "none" && parseFloat(cs.outlineWidth) >= 2;
  }
  const rr = el.getBoundingClientRect();
  const clipped = rr.width <= 1 && rr.height <= 1;
  // An outline on a 1px clipped element is no indicator at all, so a
  // visually hidden control only counts through its visible label.
  let indicator = !clipped && visibleOutline(el);
  let indicatorOn = "self";
  if (!indicator && el.id) {
    const label = document.querySelector('label[for="' + el.id + '"]');
    if (label && visibleOutline(label)) { indicator = true; indicatorOn = "label"; }
  }
  // The :focus-within pattern: an ancestor may carry the indicator, which
  // is how an iframe (whose own :focus never matches in Chromium) shows one.
  if (!indicator) {
    let a = el.parentElement, depth = 0;
    while (a && depth < 4) {
      if (visibleOutline(a)) { indicator = true; indicatorOn = "ancestor"; break; }
      a = a.parentElement; depth++;
    }
  }
  const r = el.getBoundingClientRect();
  return {tag: el.tagName.toLowerCase(),
          id: el.id || "",
          cls: (el.className || "").toString().slice(0, 60),
          text: (el.labels && el.labels[0]
                 ? el.labels[0].textContent : el.textContent || "")
                .trim().slice(0, 40),
          hidden1px: r.width <= 1 && r.height <= 1,
          indicator: indicator, indicatorOn: indicatorOn};
}"""

# Disclosure equivalence audit. Scan every stylesheet for :hover rules whose
# declarations reveal content (display/visibility/opacity), then require each
# trigger to offer a non-pointer path: native activation semantics
# (button/summary/popovertarget/details/href), a focusable trigger, or a
# paired :focus/:focus-visible/:focus-within rule in the same stylesheet.
JS_HOVER_AUDIT = """() => {
  const reveal = /(display|visibility|opacity)\\s*:/;
  const findings = [];
  const cssText = [];
  for (const sheet of document.styleSheets) {
    let rules;
    try { rules = sheet.cssRules; } catch (e) { continue; }
    for (const rule of rules) {
      if (rule.cssText) cssText.push(rule.cssText);
    }
  }
  const allCss = cssText.join("\\n");
  for (const sheet of document.styleSheets) {
    let rules;
    try { rules = sheet.cssRules; } catch (e) { continue; }
    for (const rule of rules) {
      if (!rule.selectorText || !rule.selectorText.includes(":hover")) continue;
      if (!reveal.test(rule.style.cssText)) continue;
      for (const sel of rule.selectorText.split(",")) {
        if (!sel.includes(":hover")) continue;
        const trigger = sel.slice(0, sel.indexOf(":hover")).trim();
        if (!trigger) continue;
        let els;
        try { els = document.querySelectorAll(trigger); } catch (e) { continue; }
        for (const el of els) {
          const cs = getComputedStyle(el);
          if (cs.display === "none") continue;
          const nativelyActivatable =
            el.matches("button, summary, a[href], [popovertarget], details") ||
            el.querySelector("button, summary, a[href], [popovertarget]") !== null;
          const focusable = el.tabIndex >= 0;
          const focusEquivalent =
            allCss.includes(trigger + ":focus") ||
            allCss.includes(trigger + ":focus-visible") ||
            allCss.includes(trigger + ":focus-within");
          findings.push({trigger: trigger,
                         tag: el.tagName.toLowerCase(),
                         text: (el.textContent || "").trim().slice(0, 40),
                         nativelyActivatable: nativelyActivatable,
                         focusable: focusable,
                         focusEquivalent: focusEquivalent,
                         equivalent: nativelyActivatable ||
                                     (focusable && focusEquivalent)});
          if (findings.length >= 50) return findings;
        }
      }
    }
  }
  return findings;
}"""


# --------------------------------------------------------------------------
# Screen iteration. The one-file fixture shows one screen at a time behind
# CSS-only radio switches, so every per-content gate walks all of them.
# --------------------------------------------------------------------------

JS_SCREEN_IDS = ("() => [...document.querySelectorAll('input[name=screen]')]"
                 ".map(i => i.id)")


def screen_ids(page):
    return page.evaluate(JS_SCREEN_IDS)


def show_screen(page, radio_id):
    page.evaluate("id => { document.getElementById(id).checked = true; }",
                  radio_id)


# --------------------------------------------------------------------------
# Gates
# --------------------------------------------------------------------------

def record(results, gate, state, detail):
    results.append({"gate": gate, "state": state, "detail": detail})
    print("%s: %s -- %s" % (state.upper(), gate,
                            detail if isinstance(detail, str)
                            else json.dumps(detail)[:200]))


def check_widths(browser, url, results, shots):
    for width in WIDTHS + (ZOOM_WIDTH,):
        gate = ("zoom-200-reflow" if width == ZOOM_WIDTH
                else "width-%d" % width)
        page = browser.new_page(viewport={"width": width, "height": 900})
        page.goto(url)
        overflowing = []
        for sid in screen_ids(page):
            show_screen(page, sid)
            m = page.evaluate(JS_OVERFLOW)
            if m["scrollWidth"] > m["innerWidth"] + 1:
                overflowing.append({"screen": sid,
                                    "scrollWidth": m["scrollWidth"],
                                    "innerWidth": m["innerWidth"]})
        detail = {"viewport": width, "screens": len(screen_ids(page)),
                  "overflowing_screens": overflowing}
        if shots:
            show_screen(page, screen_ids(page)[0])
            shot = os.path.join(shots, "fixture-%d.png" % width)
            page.screenshot(path=shot, full_page=False)
            detail["screenshot_sha256"] = sha256_of(shot)
        if overflowing:
            detail["reason"] = ("%d screens overflow horizontally at %dpx"
                                % (len(overflowing), width))
            record(results, gate, "fail", detail)
        else:
            record(results, gate, "pass", detail)
        page.close()


def check_keyboard(browser, url, results):
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.goto(url)
    total_stops, missing, trapped_on = 0, [], None
    for sid in screen_ids(page):
        show_screen(page, sid)
        page.evaluate("() => { if (document.activeElement) "
                      "document.activeElement.blur(); }")
        first = None
        stops = 0
        for _ in range(150):
            page.keyboard.press("Tab")
            info = page.evaluate(JS_FOCUS_INFO)
            if info.get("tag") == "body":
                continue
            key = (info.get("tag"), info.get("id"), info.get("text"))
            if first is None:
                first = key
            elif key == first:
                break
            stops += 1
            if not info.get("indicator"):
                missing.append({"screen": sid, "tag": info.get("tag"),
                                "id": info.get("id"),
                                "text": info.get("text")})
        else:
            trapped_on = sid
            break
        total_stops += stops
    detail = {"stops": total_stops,
              "without_visible_focus": missing[:20]}
    if trapped_on:
        detail["reason"] = ("focus never cycled back to the first stop on "
                            "screen %s" % trapped_on)
        record(results, "keyboard-order-and-focus", "fail", detail)
    elif missing:
        detail["reason"] = ("%d focus stops have no visible indicator "
                            "(outline >= 2px on the element or its label)"
                            % len(missing))
        record(results, "keyboard-order-and-focus", "fail", detail)
    elif not total_stops:
        record(results, "keyboard-order-and-focus", "fail",
               {"reason": "no focusable stop was reached"})
    else:
        record(results, "keyboard-order-and-focus", "pass", detail)
    page.close()


def check_targets(browser, url, results):
    page = browser.new_page(viewport={"width": 768, "height": 900})
    page.goto(url)
    targets = []
    for sid in screen_ids(page):
        show_screen(page, sid)
        for t in page.evaluate(JS_TARGETS):
            t["screen"] = sid
            targets.append(t)
    small = [t for t in targets if not t["inline"]
             and (t["w"] < MIN_TARGET or t["h"] < MIN_TARGET)]
    inline_small = [t for t in targets if t["inline"]
                    and (t["w"] < MIN_TARGET or t["h"] < MIN_TARGET)]
    detail = {"measured": len(targets),
              "inline_exempt_under_44": len(inline_small),
              "under_44": small[:20]}
    if small:
        detail["reason"] = ("%d non-inline controls measure under %dpx"
                            % (len(small), MIN_TARGET))
        record(results, "targets-44px", "fail", detail)
    else:
        record(results, "targets-44px", "pass", detail)
    page.close()


def check_contrast(browser, fixture_url, oled_url, results):
    legs = (("contrast-light", fixture_url, "light"),
            ("contrast-dark", fixture_url, "dark"),
            ("contrast-oled", oled_url, "light"))
    for gate, url, scheme in legs:
        page = browser.new_page(viewport={"width": 1280, "height": 900},
                                color_scheme=scheme)
        page.goto(url)
        samples = []
        for sid in screen_ids(page):
            show_screen(page, sid)
            for s in page.evaluate(JS_CONTRAST):
                s["screen"] = sid
                samples.append(s)
        low = [s for s in samples
               if s["ratio"] < (MIN_LARGE_CONTRAST if s["large"]
                                else MIN_TEXT_CONTRAST)]
        detail = {"sampled": len(samples),
                  "min_ratio": min((s["ratio"] for s in samples), default=None),
                  "below_aa": low[:20]}
        if low:
            detail["reason"] = "%d text samples fall below WCAG AA" % len(low)
            record(results, gate, "fail", detail)
        else:
            record(results, gate, "pass", detail)
        page.close()


def check_reduced_motion(browser, url, results):
    page = browser.new_page(viewport={"width": 1280, "height": 900},
                            reduced_motion="reduce")
    page.goto(url)
    count = page.evaluate("() => document.getAnimations().length")
    if count:
        record(results, "reduced-motion", "fail",
               {"running_animations": count,
                "reason": "animations run under prefers-reduced-motion"})
    else:
        record(results, "reduced-motion", "pass", {"running_animations": 0})
    page.close()


def check_touch_disclosure(browser, url, results):
    context = browser.new_context(viewport={"width": 768, "height": 900},
                                  has_touch=True)
    page = context.new_page()
    page.goto(url)
    trigger = None
    for sid in screen_ids(page):
        show_screen(page, sid)
        for candidate in page.query_selector_all("[popovertarget]"):
            if candidate.is_visible():
                trigger = candidate
                break
        if trigger is not None:
            break
    if trigger is None:
        record(results, "touch-disclosure", "fail",
               {"reason": "no popover disclosure trigger found"})
    else:
        target_id = trigger.get_attribute("popovertarget")
        trigger.scroll_into_view_if_needed()
        trigger.tap()
        opened = page.evaluate(
            "id => { const el = document.getElementById(id);"
            "  return !!el && el.matches(':popover-open'); }", target_id)
        if opened:
            record(results, "touch-disclosure", "pass",
                   {"trigger": trigger.text_content().strip()[:40],
                    "target": target_id})
        else:
            record(results, "touch-disclosure", "fail",
                   {"target": target_id,
                    "reason": "tapping the disclosure trigger did not open "
                              "its definition"})
    context.close()


def check_static_fallback(browser, url, results):
    context = browser.new_context(java_script_enabled=False,
                                  viewport={"width": 1280, "height": 900})
    page = context.new_page()
    page.goto(url)
    scripts = page.evaluate("() => document.querySelectorAll('script').length")
    empty_screens, text_total = [], 0
    for sid in screen_ids(page):
        show_screen(page, sid)
        text_len = page.evaluate("() => document.body.innerText.length")
        text_total += text_len
        if text_len < 300:
            empty_screens.append(sid)
    headings = page.evaluate(
        "() => document.querySelectorAll('h1, h2, h3').length")
    detail = {"script_elements": scripts, "text_chars_across_screens":
              text_total, "headings": headings,
              "screens_with_under_300_chars": empty_screens}
    if scripts == 0 and not empty_screens and headings >= 3:
        record(results, "static-fallback", "pass", detail)
    else:
        detail["reason"] = ("the fixture must stay script-free and fully "
                            "readable without JavaScript on every screen")
        record(results, "static-fallback", "fail", detail)
    context.close()


def check_equivalence(browser, url, results, gate, expect_failure):
    """The disclosure equivalence audit, run positively on the fixture and
    negatively on the hover-only page. The negative page passing would mean
    the audit cannot catch the one failure mode it exists for."""
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.goto(url)
    findings = page.evaluate(JS_HOVER_AUDIT)
    inequivalent = [f for f in findings if not f["equivalent"]]
    detail = {"hover_reveal_triggers": len(findings),
              "without_equivalent": inequivalent[:10]}
    if expect_failure:
        if inequivalent:
            detail["reason"] = ("hover-only disclosure has no keyboard or "
                                "touch equivalent; fails equivalence review "
                                "as required")
            record(results, gate, "fail", detail)
        else:
            record(results, gate, "pass",
                   dict(detail, reason="the deliberately hover-only fixture "
                        "was not caught; the audit is broken"))
    else:
        if inequivalent:
            detail["reason"] = ("%d hover-revealed disclosures lack a "
                                "keyboard or touch equivalent"
                                % len(inequivalent))
            record(results, gate, "fail", detail)
        else:
            record(results, gate, "pass", detail)
    page.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", dest="json_path",
                        help="write the evidence JSON here ('-' for stdout)")
    parser.add_argument("--shots", dest="shots",
                        help="write screenshots into this directory")
    args = parser.parse_args()

    if args.shots:
        os.makedirs(args.shots, exist_ok=True)

    results = []
    work = tempfile.mkdtemp(prefix="visual_qa_")
    fixture, oled, negative = build_pages(work)

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            from importlib.metadata import version
            pw_version = version("playwright")
        except Exception:
            pw_version = "unknown"
        env = {"playwright": pw_version,
               "browser": browser.version,
               "direction": visual_fixture.DEFAULT_DIRECTION}
        check_widths(browser, file_url(fixture), results, args.shots)
        check_keyboard(browser, file_url(fixture), results)
        check_targets(browser, file_url(fixture), results)
        check_contrast(browser, file_url(fixture), file_url(oled), results)
        check_reduced_motion(browser, file_url(fixture), results)
        check_touch_disclosure(browser, file_url(fixture), results)
        check_static_fallback(browser, file_url(fixture), results)
        check_equivalence(browser, file_url(fixture), results,
                          "fixture-disclosure-equivalence",
                          expect_failure=False)
        check_equivalence(browser, file_url(negative), results,
                          "hover-only-negative", expect_failure=True)
        browser.close()

    negative_rows = [r for r in results if r["gate"] == "hover-only-negative"]
    positive_rows = [r for r in results if r["gate"] != "hover-only-negative"]
    positives_ok = all(r["state"] == "pass" for r in positive_rows)
    negative_ok = bool(negative_rows) and all(
        r["state"] == "fail" for r in negative_rows)

    evidence = {"harness": env, "results": results,
                "matrix_as_expected": positives_ok and negative_ok}
    if args.json_path == "-":
        print(json.dumps(evidence, indent=2))
    elif args.json_path:
        with open(args.json_path, "w", encoding="utf-8") as fh:
            json.dump(evidence, fh, indent=2)
            fh.write("\n")

    if positives_ok and negative_ok:
        print("PASS visual_qa matrix: %d positive gates green, the hover-only "
              "negative fixture failed equivalence review as required"
              % len(positive_rows))
        return 0
    if not negative_ok:
        print("FAIL visual_qa: the deliberately hover-only fixture did not "
              "fail equivalence review")
    failed = [r["gate"] for r in positive_rows if r["state"] != "pass"]
    if failed:
        print("FAIL visual_qa gates: " + ", ".join(failed))
    return 1


if __name__ == "__main__":
    sys.exit(main())
