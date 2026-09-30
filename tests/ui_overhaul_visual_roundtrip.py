#!/usr/bin/env python3
"""Bounded visual-system contracts and same-content synthetic comparisons."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from surfaces import presentation, theme, looks

BODY = '''<nav aria-label="Synthetic journey" class="course-areas"><ul>
<li><a href="#home">Home</a></li><li><a href="#course">Course</a></li>
<li><a href="#reading">Read</a></li><li><a href="#practice">Practice</a></li></ul></nav>
<section id="home" class="overhaul-lead"><p class="desk-eyebrow">SYNTHETIC COURSE JOURNEY</p>
<h2>Small observations, clear explanations</h2><p>Explore how a claim grows from evidence. This local comparison uses fictional content and stores no learner data.</p>
<div class="actions"><a class="go primary" href="#course">Open the course</a></div></section>
<section id="course"><h2>Your next activity</h2><p>Read a short observation, keep your own note, then try a question. No progress or mastery is implied.</p>
<div class="actions"><a class="go" href="#reading">Read the observation</a><a class="go" href="#practice">Try a question</a></div></section>
<div class="overhaul-journey"><section id="reading" class="overhaul-source"><h2>Source observation</h2>
<div class="overhaul-prose"><p>In a fictional garden, two seedlings received the same amount of water. One stood by a window; the other stood on a shaded shelf.</p>
<p>After a week, the window seedling had three new leaves. The shaded seedling had one. This observation gives us a question, not a universal rule.</p>
<p>观察与解释: an observation records what happened; an explanation proposes why.</p></div>
<p class="ib-source">Source: fictional workshop excerpt, revision 1. A source citation remains visible even without scripts.</p></section>
<aside class="overhaul-notes"><h2>Private note</h2><p>Your note is separate from source claims and assessed answers.</p>
<label for="comparison-note">What would you check next?</label><textarea id="comparison-note">I would repeat the observation with more seedlings.</textarea></aside></div>
<section id="practice"><h2>Practice response</h2><p>Which next step would help test an explanation? This preview does not score your choice.</p>
<fieldset class="overhaul-response"><legend>Choose a next step</legend>
<label><input type="radio" name="comparison" value="repeat">Repeat the observation with more seedlings</label>
<label><input type="radio" name="comparison" value="conclude">Declare that all plants grow faster near windows</label></fieldset>
<p class="state">Preview only. A served sitting uses the runtime for feedback and scoring.</p>
<details class="details-section"><summary>Review the source</summary><a class="go" href="#reading">Return to the observation</a></details></section>'''

QUIET_CSS = '''
.surface,.surface.wide{max-width:800px}
.overhaul-journey{display:block}
.overhaul-lead{background:transparent;border:0;padding:var(--space-5) 0}
.overhaul-lead h2{font-family:var(--font-paper)}
.overhaul-source{background:transparent;border:0;padding:var(--space-4) 0}
.overhaul-notes{background:transparent;border:0;border-top:1px solid var(--line);padding:var(--space-4) 0}
.overhaul-response{background:transparent;border:0;border-top:1px solid var(--edge);border-radius:0}
'''


def comparison_page(direction, mode='light', accent=theme.DEFAULT_ACCENT):
    return presentation.surface_shell(
        'Learning workshop', BODY,
        theme_css=theme.theme_css({'theme': mode, 'accent': {'source': accent}}),
        extra_css=QUIET_CSS if direction == 'quiet' else '',
        noscript='This synthetic preview remains readable without scripts.')


def check_contracts():
    css = presentation.PRODUCT_CSS
    assert '224px' not in css, 'old rail still consumes activity space'
    assert '.product-sidebar{position:sticky' in css
    assert 'min-height:70px' in css and 'height:70px;' not in css.replace('min-height:70px;', '')
    assert 'overflow-x:hidden' not in css and 'white-space:nowrap' not in css
    for role in ('source', 'notes', 'response'):
        assert '.overhaul-' + role in css
    assert 'max-width:var(--measure-prose)' in css
    assert 'prefers-reduced-motion:reduce' in css
    for mode in ('light', 'dark', 'oled', 'system'):
        for look in looks.LOOK_IDS:
            config = {'theme': mode, 'look': look, 'accent': {'source': '#ff0000'}}
            tokens = theme.theme_css(config)
            assert 'color-scheme:' in tokens
            if mode in ('dark', 'oled'):
                assert 'color-scheme:dark' in tokens
            for direction in ('quiet', 'workshop'):
                page = comparison_page(direction, mode, '#ff0000')
                for target in ('/', '/courses', '/activity', '/settings'):
                    assert 'href="%s"' % target in page
                assert page.count('<h1>') == 1
                assert '<noscript>' in page and 'focus-visible' in page
    quiet, workshop = comparison_page('quiet'), comparison_page('workshop')
    assert re.search(r'<main>(.*?)</main>', quiet, re.S).group(1) == BODY
    assert re.search(r'<main>(.*?)</main>', workshop, re.S).group(1) == BODY
    assert quiet != workshop, 'comparison accidentally has one treatment'
    print('visual overhaul: compact frame, theme/native controls, role separation, same-content comparison passed')


def write_previews():
    directory = ROOT / 'prototypes/ui-overhaul-20260930/visual'
    directory.mkdir(parents=True, exist_ok=True)
    for direction in ('quiet', 'workshop'):
        for mode in ('light', 'dark'):
            (directory / ('%s-%s.html' % (direction, mode))).write_text(comparison_page(direction, mode))
    (directory / 'workshop-custom.html').write_text(comparison_page('workshop', 'light', '#0e6e62'))
    (directory / 'README.md').write_text('''# Visual comparison

Both directions use identical fictional course-journey content and controls.
Quiet reading uses a single measured column, open section rhythm and minimal
panel grounds. Expressive workshop uses a wider activity canvas, an accent
entry panel and separate source/private-note columns. Workshop is the reversible
working direction because it makes concurrent reading and note-taking visible;
this is a design rationale, not evidence of user preference.

Generate with `python3 tests/ui_overhaul_visual_roundtrip.py --previews`.
Serve this directory locally and inspect `quiet-light.html` and
`workshop-light.html`; dark and custom-accent variants exercise the same content.
These are presentation comparisons, not scored sittings or durable course files.
The browser checker is `verify.mjs`, with optional `ITEMBANK_PLAYWRIGHT_MODULE`
and `ITEMBANK_CHROMIUM` environment paths. It owns and stops its static server.
''')


if __name__ == '__main__':
    check_contracts()
    if '--previews' in sys.argv:
        write_previews()
