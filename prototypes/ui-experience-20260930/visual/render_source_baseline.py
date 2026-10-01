"""Generate a fresh current-source shell over the same synthetic lesson."""
import hashlib
import json
import re
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from surfaces import presentation, theme
html = (HERE / 'index.html').read_text()
body = re.search(r'<main[^>]*>(.*?)</main>', html, re.S).group(1)
body = re.sub(r'<div class="title-row">.*?</div>', '', body, flags=re.S)
body = body.replace('class="reading"', 'class="reading overhaul-prose"')
body = body.replace('class="source"', 'class="source overhaul-source"')
body = body.replace('class="note"', 'class="note overhaul-notes"')
body = body.replace('class="context"', 'class="context overhaul-journey"')
body = body.replace('class="prediction"', 'class="prediction overhaul-response"')
body = body.replace('class="primary"', 'class="go primary"')
body = body.replace('<button', '<button disabled')
css = '''
.intro,.reading,.experiment,.prediction,.context,.next{margin-bottom:32px}
.reading p{font:18px/1.65 var(--font-paper)}
.eyebrow,.locator{font:12px/1.5 var(--font-ledger);color:var(--mut)}
.experiment{padding:24px;border:1px solid var(--line);border-radius:8px}
.experiment-head,.readouts>div{display:flex;justify-content:space-between;gap:16px}
svg{display:block;width:100%;max-width:640px;margin:auto;color:var(--ink)}
.grid{display:none}.track{stroke:var(--line);stroke-width:2}.travel{fill:none;stroke-width:4}
.a{stroke:var(--source-mark);color:var(--source-mark)}.b{stroke:var(--note-mark);color:var(--note-mark)}
.walker{stroke-width:3;stroke-linecap:round;fill:currentColor}.walker path{fill:none}
.scrubber input{display:block;width:100%;min-height:44px}
.range-ends{display:flex;justify-content:space-between}
fieldset{border:0}fieldset label{display:flex;align-items:center;gap:8px;min-height:44px}
.formula{padding:16px;background:var(--chip);margin:24px 0}.formula small{display:block}
.trail{display:flex;gap:24px}.trail a,.source-link,summary{display:inline-flex;align-items:center;min-height:44px}
.note label span{display:block;font-size:12px}.note textarea{width:100%;min-height:88px}
.source blockquote{margin:16px 0;font:18px/1.65 var(--font-paper)}
.next{border-top:1px solid var(--line);padding-top:24px}
'''
for mode in ('light', 'dark'):
    page = presentation.surface_shell('Same time. Different distances.', '<p class="state">Current source shell, same synthetic content. Static comparison; use candidates for interaction.</p>' + body, theme_css=theme.theme_css({'theme': mode}), extra_css=css, noscript='Static synthetic comparison.')
    (HERE / f'source-baseline-{mode}.html').write_text(page)
manifest = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'surfaces/presentation.py', ROOT/'surfaces/theme.py')}
(HERE/'baseline-source-hashes.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Generated light/dark baseline from current source; no product writes.')
