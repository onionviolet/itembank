"""The look axis: shape, type and control language, switchable per install.

A look is not a theme and not an accent. `theme` is light, dark, oled or
system; `accent` is one persisted source colour every mode derives from
(`surfaces/theme.py` owns both, and stays the only palette authority). A
look is the third axis Weibao asked for on 2026-09-05, after reviewing the
rendered screens and finding the app "not clean enough or smooth enough,
feels generic": the radii, the type scale and tracking, the density, the
button and nav language, and the ground the palette sits on.

Three rules keep this from becoming a second design system:

1. **A look never invents a colour a surface reads as meaning.** The
   semantic tokens (ok, bad, warn, unknown, pending, edge) stay exactly
   where they are, in `theme.SEMANTIC_TOKENS`, fixed per mode. A look may
   move the GROUND those are measured against, which is why every look's
   grounds are re-measured against every semantic token by
   `tests/stylesheet_roundtrip.py` on every run, at the same 4.5:1 text and
   3:1 non-text floors. A look that fails is a look that does not ship.
2. **A look never changes what a control does or says.** No copy, no
   route, no order, no state. If a look could change what a learner
   understands, it is not a look.
3. **A look's accent and preferred mode are defaults, not locks.** Picking
   a look writes its accent and its mode into settings once, through the
   one persistence path; the learner may then change either independently
   and the look stays as it is.

`css` blocks are shape only: radii, spacing, type, weight, tracking,
borders, shadows, and control geometry. Every colour in them resolves
through a token, never a literal, with the single exception of the shadow
alphas, which are a shape property of a raised surface and are declared by
the look that raises it.
"""

# Ordered. The order is the order a picker lists them in, so it is a
# published sequence rather than a dict's insertion accident: the shipped
# look first, then the five directions rendered for Weibao on 2026-09-05,
# then the accessibility-first one.
LOOK_IDS = ("classic", "editorial", "neo", "cash", "console", "soft",
            "contrast")

DEFAULT_LOOK = "classic"

# The shape vocabulary every look below composes from. Named here so a look
# is a set of values rather than a set of rules, and so two looks that want
# the same radius cannot drift by a pixel.
_SHARED = """
.walkthrough-offer form,.actions{display:flex;flex-wrap:wrap;gap:10px;
  margin:16px 0 0;align-items:center}
.walkthrough-offer{margin:0 0 12px}
.walkthrough-replay{margin:0 0 10px}
.confirm-copy{display:block;color:var(--mut);font-size:var(--text-xs);
  margin-top:var(--space-2)}
.sample-note{color:var(--mut);font-size:13px;margin:var(--space-2) 0 0}
.resume-cue{margin:var(--space-2) 0 0;color:var(--mut)}
.course-card h2{margin:0 0 var(--space-2)}
"""

LOOKS = {
    "classic": {
        "name": "Classic",
        "blurb": "The shipped look: bordered cards, system type, 8px radii.",
        "mode": None,
        "accent": None,
        "grounds": {},
        "css": "",
    },
    "editorial": {
        "name": "Editorial",
        "blurb": "Paper and hairlines. Serif display, mono meta, one solid "
                 "control, boxes only where a box means something.",
        "mode": "light",
        "accent": "#0f5c53",
        "grounds": {
            "light": {"bg": "#fbfbfa", "card": "#ffffff", "ink": "#14161a",
                      "chip": "#f2f2f0", "line": "#e4e4e1", "mut": "#5d646d"},
        },
        "css": """
body{letter-spacing:-.011em}
.surface{max-width:760px;padding:var(--space-6) var(--space-4) var(--space-7)}
h1{font-family:var(--font-paper);font-size:40px;font-weight:600;
  letter-spacing:-.025em;line-height:1.08;margin:0 0 var(--space-1)}
h2{font-family:var(--font-paper);font-size:23px;font-weight:600;
  letter-spacing:-.018em;margin:var(--space-5) 0 var(--space-3)}
h3{font-size:13px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;
  color:var(--mut);margin:var(--space-4) 0 var(--space-2)}
a{text-decoration:none;font-weight:550}
a:hover{text-decoration:underline;text-underline-offset:3px}
.card,.row,.course-card,.state,.empty,.step{background:transparent;border:0;
  border-top:1px solid var(--line);border-radius:0;
  padding:var(--space-3) 0 var(--space-4);box-shadow:none}
.card{border:1px solid var(--line);border-radius:2px;background:var(--card);
  padding:var(--space-5) var(--space-5) var(--space-4)}
.stem{font-family:var(--font-paper);font-size:27px;line-height:1.22;
  letter-spacing:-.02em;font-weight:600;margin:0 0 var(--space-4)}
.chip{background:transparent;border:0;padding:0;font-family:var(--font-ledger);
  font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--mut)}
a.go,button.go,.walkthrough-offer button,form[data-shelf-form] button{
  background:var(--ink);color:var(--bg);border:1px solid var(--ink);
  border-radius:2px;padding:11px 18px;font-weight:600;font-size:16px;
  text-decoration:none;box-shadow:none}
a.go.ghost,button.go.ghost,.walkthrough-replay button,
form[data-shelf-form] button[value="skip_walkthrough"],
form[data-shelf-form] button[value="remove_sample_course"]{
  background:transparent;color:var(--ink);border:1px solid var(--edge)}
.hint-card{border:0;border-top:1px solid var(--line);border-radius:0;
  padding:var(--space-3) 0}
.course-areas ul{display:flex;flex-wrap:wrap;gap:0 22px;list-style:none;
  padding:0 0 var(--space-3);margin:0 0 var(--space-3);
  border-bottom:1px solid var(--line)}
.course-areas a{font-size:13px;font-weight:550;color:var(--mut)}
.course-areas a[aria-current]{color:var(--ink);text-decoration:underline;
  text-underline-offset:6px;text-decoration-thickness:2px}
""",
    },
    "neo": {
        "name": "Neo",
        "blurb": "App register. Rounded surfaces, pill controls, heavy "
                 "display type, one saturated accent, plenty of air.",
        "mode": "light",
        "accent": "#1e46c8",
        "grounds": {
            "light": {"bg": "#f4f5f7", "card": "#ffffff", "ink": "#0b0d12",
                      "chip": "#eceef3", "line": "#e2e5ec", "mut": "#5b6270"},
        },
        "css": """
body{letter-spacing:-.014em}
.surface{max-width:760px;padding:var(--space-6) var(--space-3) var(--space-7)}
h1{font-size:44px;font-weight:800;letter-spacing:-.04em;line-height:1.02;
  margin:0 0 var(--space-2)}
h2{font-size:24px;font-weight:750;letter-spacing:-.03em;
  margin:var(--space-5) 0 var(--space-3)}
h3{font-size:15px;font-weight:700;color:var(--ink);
  margin:var(--space-4) 0 var(--space-2)}
a{font-weight:600;text-decoration:none}
.card,.row,.course-card,.state,.empty,.step{background:var(--card);border:0;
  border-radius:22px;padding:var(--space-4);
  box-shadow:0 1px 2px rgba(11,13,18,.05),0 8px 24px rgba(11,13,18,.05)}
.course-shelf{display:grid;gap:var(--space-3)}
.card{padding:var(--space-5) var(--space-5) var(--space-4)}
.stem{font-size:29px;font-weight:750;letter-spacing:-.032em;line-height:1.18;
  margin:0 0 var(--space-4);font-family:var(--font-chrome)}
.chip{background:var(--chip);color:var(--mut);border:0;border-radius:999px;
  padding:6px 12px;font-size:12px;font-weight:650;text-transform:none;
  letter-spacing:0;font-family:var(--font-chrome)}
a.go,button.go,.walkthrough-offer button,form[data-shelf-form] button{
  background:var(--accent);color:var(--card);border:0;border-radius:999px;
  padding:14px 22px;font-weight:650;font-size:16px;text-decoration:none}
a.go.ghost,button.go.ghost,.walkthrough-replay button,
form[data-shelf-form] button[value="skip_walkthrough"],
form[data-shelf-form] button[value="remove_sample_course"]{
  background:var(--chip);color:var(--ink);border:0}
.choice{background:var(--card);border:1.5px solid var(--line);
  border-radius:16px;padding:var(--space-3)}
.hint-card{background:var(--chip);border:0;border-radius:16px;
  padding:var(--space-3)}
.course-rows{gap:var(--space-3)}
.course-areas ul{list-style:none;padding:0;margin:0 0 var(--space-3);
  display:flex;flex-wrap:wrap;gap:var(--space-2)}
.course-areas a{display:inline-block;background:var(--chip);color:var(--mut);
  border-radius:999px;padding:8px 14px;font-size:14px;font-weight:600}
.course-areas a[aria-current]{background:var(--ink);color:var(--bg)}
""",
    },
    "cash": {
        "name": "Cash",
        "blurb": "Dark and loud. Oversized type, no borders anywhere, one "
                 "bright accent doing all the pointing.",
        "mode": "dark",
        "accent": "#12b356",
        "grounds": {
            "dark": {"bg": "#0a0a0b", "card": "#151518", "ink": "#f7f7f8",
                     "chip": "#1e1f24", "line": "#2a2b31", "mut": "#9096a1"},
            "oled": {"bg": "#000000", "card": "#0c0c0e", "ink": "#f7f7f8",
                     "chip": "#16171a", "line": "#212227", "mut": "#9096a1"},
        },
        "css": """
body{letter-spacing:-.02em}
.surface{max-width:740px;padding:var(--space-5) var(--space-3) var(--space-7)}
h1{font-size:52px;font-weight:800;letter-spacing:-.045em;line-height:.98;
  margin:0 0 var(--space-3)}
h2{font-size:26px;font-weight:750;letter-spacing:-.035em;
  margin:var(--space-5) 0 var(--space-3)}
h3{font-size:14px;font-weight:700;color:var(--mut);
  margin:var(--space-4) 0 var(--space-2)}
a{font-weight:650;text-decoration:none}
.card,.row,.course-card,.state,.empty,.step{background:var(--card);border:0;
  border-radius:24px;padding:var(--space-4);box-shadow:none}
.course-shelf{display:grid;gap:var(--space-3)}
.card{padding:var(--space-5) var(--space-5) var(--space-4)}
.stem{font-size:30px;font-weight:750;letter-spacing:-.035em;line-height:1.15;
  margin:0 0 var(--space-4)}
.chip{background:transparent;color:var(--accent);border:0;padding:0;
  font-size:13px;font-weight:700;text-transform:none;letter-spacing:0;
  font-family:var(--font-chrome)}
a.go,button.go,.walkthrough-offer button,form[data-shelf-form] button{
  background:var(--accent);color:var(--bg);border:0;border-radius:999px;
  padding:16px 26px;font-size:16px;font-weight:750;text-decoration:none}
a.go.ghost,button.go.ghost,.walkthrough-replay button,
form[data-shelf-form] button[value="skip_walkthrough"],
form[data-shelf-form] button[value="remove_sample_course"]{
  background:var(--chip);color:var(--ink);border:0}
.choice{background:var(--chip);border:0;border-radius:18px;padding:var(--space-3)}
.hint-card{background:var(--chip);border:0;border-radius:18px;
  padding:var(--space-3)}
.course-rows{gap:var(--space-3)}
.course-areas ul{list-style:none;padding:0;margin:0 0 var(--space-3);
  display:flex;flex-wrap:wrap;gap:var(--space-2)}
.course-areas a{display:inline-block;background:var(--chip);color:var(--mut);
  border-radius:999px;padding:9px 15px;font-size:14px;font-weight:650}
.course-areas a[aria-current]{background:var(--accent);color:var(--bg)}
""",
    },
    "console": {
        "name": "Console",
        "blurb": "Dark, dense and gridded. Every card on a left rail, mono "
                 "labels, tight rhythm.",
        "mode": "dark",
        "accent": "#1aa08d",
        "grounds": {
            "dark": {"bg": "#0c0d0f", "card": "#131519", "ink": "#e9eaec",
                     "chip": "#1a1d22", "line": "#272b31", "mut": "#8b9099"},
        },
        "css": """
body{letter-spacing:-.008em}
.surface{max-width:820px;padding:var(--space-5) var(--space-3) var(--space-7)}
h1{font-size:34px;font-weight:700;letter-spacing:-.03em;line-height:1.1;
  margin:0 0 var(--space-1)}
h2{font-size:19px;font-weight:650;letter-spacing:-.02em;
  margin:var(--space-5) 0 var(--space-3)}
h3{font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;
  color:var(--mut);margin:var(--space-4) 0 var(--space-2)}
a{font-weight:550;text-decoration:none}
.card,.row,.course-card,.state,.empty,.step{background:var(--card);
  border:1px solid var(--line);border-left:2px solid var(--edge);
  border-radius:3px;padding:var(--space-3)}
.course-card{border-left:2px solid var(--accent)}
.card{padding:var(--space-4) var(--space-4) var(--space-3)}
.stem{font-family:var(--font-paper);font-size:25px;line-height:1.25;
  font-weight:600;letter-spacing:-.015em;margin:0 0 var(--space-3)}
.chip{background:var(--chip);border:1px solid var(--line);border-radius:2px;
  padding:3px 7px;font-family:var(--font-ledger);font-size:11px;
  letter-spacing:.1em;text-transform:uppercase;color:var(--mut)}
a.go,button.go,.walkthrough-offer button,form[data-shelf-form] button{
  background:var(--accent);color:var(--bg);border:1px solid var(--accent);
  border-radius:3px;padding:10px 16px;font-weight:650;font-size:16px;
  text-decoration:none}
a.go.ghost,button.go.ghost,.walkthrough-replay button,
form[data-shelf-form] button[value="skip_walkthrough"],
form[data-shelf-form] button[value="remove_sample_course"]{
  background:transparent;color:var(--ink);border:1px solid var(--edge)}
.hint-card{background:var(--card);border:1px solid var(--line);
  border-left:2px solid var(--edge);border-radius:3px;padding:var(--space-3)}
.course-rows{gap:var(--space-2)}
.course-areas ul{display:flex;flex-wrap:wrap;gap:0 18px;list-style:none;
  padding:0 0 var(--space-3);margin:0 0 var(--space-3);
  border-bottom:1px solid var(--line)}
.course-areas a{font-size:13px;color:var(--mut);font-weight:550}
.course-areas a[aria-current]{color:var(--accent)}
""",
    },
    "soft": {
        "name": "Soft",
        "blurb": "Warm paper, rounded corners, serif display over a quiet "
                 "sans. The calmest of the set for long reading.",
        "mode": "light",
        "accent": "#9c3d18",
        "grounds": {
            # `chip` is #f4f0e8 and not the #f1ece3 this look was sketched
            # with: the sketch measured --edge against it at 2.999:1, three
            # thousandths under WCAG 1.4.11's 3:1 for a boundary that
            # identifies a control. Measured, not nudged by eye; the fixture
            # re-measures it on every run.
            "light": {"bg": "#faf7f2", "card": "#fffdfa", "ink": "#241f1a",
                      "chip": "#f4f0e8", "line": "#e7ded0", "mut": "#6b6053"},
        },
        "css": """
body{letter-spacing:-.008em}
.surface{max-width:720px;padding:var(--space-6) var(--space-3) var(--space-7)}
h1{font-family:var(--font-paper);font-size:42px;font-weight:600;
  letter-spacing:-.022em;line-height:1.06;margin:0 0 var(--space-2)}
h2{font-family:var(--font-paper);font-size:25px;font-weight:600;
  letter-spacing:-.015em;margin:var(--space-5) 0 var(--space-3)}
h3{font-size:14px;font-weight:650;color:var(--mut);
  margin:var(--space-4) 0 var(--space-2)}
p{line-height:1.6}
a{font-weight:600;text-decoration:none}
.card,.row,.course-card,.state,.empty,.step{background:var(--card);
  border:1px solid var(--line);border-radius:18px;padding:var(--space-4);
  box-shadow:0 1px 0 rgba(36,31,26,.03)}
.course-shelf{display:grid;gap:var(--space-3)}
.card{padding:var(--space-5) var(--space-5) var(--space-4)}
.stem{font-family:var(--font-paper);font-size:28px;font-weight:600;
  letter-spacing:-.018em;line-height:1.22;margin:0 0 var(--space-3)}
.chip{background:var(--chip);color:var(--mut);border:0;border-radius:999px;
  padding:5px 12px;font-size:12px;font-weight:600;text-transform:none;
  letter-spacing:0;font-family:var(--font-chrome)}
a.go,button.go,.walkthrough-offer button,form[data-shelf-form] button{
  background:var(--ink);color:var(--card);border:0;border-radius:14px;
  padding:13px 20px;font-weight:650;font-size:16px;text-decoration:none}
a.go.ghost,button.go.ghost,.walkthrough-replay button,
form[data-shelf-form] button[value="skip_walkthrough"],
form[data-shelf-form] button[value="remove_sample_course"]{
  background:var(--chip);color:var(--ink);border:0}
.choice{background:var(--card);border:1px solid var(--line);border-radius:14px;
  padding:var(--space-3)}
.hint-card{background:var(--chip);border:0;border-radius:14px;
  padding:var(--space-3)}
.course-rows{gap:var(--space-3)}
.course-areas ul{list-style:none;padding:0;margin:0 0 var(--space-3);
  display:flex;flex-wrap:wrap;gap:var(--space-2)}
.course-areas a{display:inline-block;background:var(--chip);color:var(--mut);
  border-radius:999px;padding:8px 14px;font-size:14px;font-weight:600}
.course-areas a[aria-current]{background:var(--accent);color:var(--card)}
""",
    },
    "contrast": {
        "name": "High contrast",
        "blurb": "Maximum separation: black on white, heavy rules, square "
                 "corners, thick focus. For low vision and bright rooms.",
        "mode": "light",
        "accent": "#0b4f8a",
        "grounds": {
            "light": {"bg": "#ffffff", "card": "#ffffff", "ink": "#000000",
                      "chip": "#f0f0f0", "line": "#000000", "mut": "#3a3a3a"},
        },
        "css": """
body{letter-spacing:0}
.surface{max-width:760px;padding:var(--space-5) var(--space-3) var(--space-7)}
h1{font-size:38px;font-weight:800;line-height:1.1;margin:0 0 var(--space-2)}
h2{font-size:24px;font-weight:750;margin:var(--space-5) 0 var(--space-3)}
h3{font-size:16px;font-weight:750;margin:var(--space-4) 0 var(--space-2)}
p,body{font-size:17px}
a{font-weight:700;text-decoration:underline;text-underline-offset:3px}
.card,.row,.course-card,.state,.empty,.step,.choice,.hint-card{
  background:var(--card);border:2px solid var(--ink);border-radius:0;
  padding:var(--space-3);box-shadow:none}
.card{padding:var(--space-4)}
.stem{font-size:28px;font-weight:750;line-height:1.25;margin:0 0 var(--space-3)}
.chip{background:var(--chip);color:var(--ink);border:2px solid var(--ink);
  border-radius:0;padding:2px 8px;font-size:13px;font-weight:700;
  text-transform:none;letter-spacing:0}
a.go,button.go,.walkthrough-offer button,form[data-shelf-form] button{
  background:var(--ink);color:var(--card);border:2px solid var(--ink);
  border-radius:0;padding:12px 18px;font-weight:750;font-size:16px;
  text-decoration:none}
a.go.ghost,button.go.ghost,.walkthrough-replay button,
form[data-shelf-form] button[value="skip_walkthrough"],
form[data-shelf-form] button[value="remove_sample_course"]{
  background:var(--card);color:var(--ink);border:2px solid var(--ink)}
a:focus-visible,button:focus-visible,summary:focus-visible,
input:focus-visible,textarea:focus-visible,select:focus-visible{
  outline:4px solid var(--accent);outline-offset:2px}
.course-areas ul{list-style:none;padding:0;margin:0 0 var(--space-3);
  display:flex;flex-wrap:wrap;gap:var(--space-2)}
.course-areas a{display:inline-block;border:2px solid var(--ink);padding:6px 12px;
  font-weight:700}
.course-areas a[aria-current]{background:var(--ink);color:var(--card)}
""",
    },
}


def known(look_id):
    """True when `look_id` names a shipped look. An unknown look is never
    guessed at or partially applied: callers fall back to DEFAULT_LOOK, which
    is the shipped shape and therefore always a safe answer."""
    return isinstance(look_id, str) and look_id in LOOKS


def resolve(look_id):
    """`look_id` if it is known, otherwise DEFAULT_LOOK."""
    return look_id if known(look_id) else DEFAULT_LOOK


def grounds_for(look_id, mode):
    """The base-token overrides this look states for `mode`, or `{}`.

    A look that states nothing for a mode renders that mode exactly as the
    shipped palette does, which is what lets a light-only look be selected
    in dark mode without inventing a dark ground nobody measured.
    """
    return dict(LOOKS[resolve(look_id)]["grounds"].get(mode, {}))


def accent_for(look_id):
    """The accent source this look suggests, or None."""
    return LOOKS[resolve(look_id)]["accent"]


def mode_for(look_id):
    """The theme mode this look was designed in, or None for either."""
    return LOOKS[resolve(look_id)]["mode"]


def look_css(look_id):
    """The look's shape block, ready to append after the token block.

    Returns "" for the shipped look, so a default install emits byte-identical
    CSS to what it emitted before this axis existed.
    """
    block = LOOKS[resolve(look_id)]["css"].strip()
    if not block:
        return ""
    return "\n".join((block, _SHARED.strip()))


def catalogue():
    """Every look as a plain dict, in LOOK_IDS order: what a picker renders
    and what `itembank theme --looks` prints."""
    return [{"id": look_id, "name": LOOKS[look_id]["name"],
             "blurb": LOOKS[look_id]["blurb"],
             "mode": LOOKS[look_id]["mode"],
             "accent": LOOKS[look_id]["accent"]}
            for look_id in LOOK_IDS]
