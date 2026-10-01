"""Compose frozen lane outputs into a coherent original synthetic preview."""
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
LANES = HERE.parent

if __name__ == '__main__':
    for lane in ('visual', 'teaching', 'workspace'):
        if not (LANES / lane / 'HANDOFF.md').exists():
            raise SystemExit('Awaiting frozen handoff: '+lane)
    source = (LANES / 'teaching/index.html').read_text()
    note = re.search(r'    <aside class="note">.*?</aside>', source, re.S).group()
    source = source.replace(note, '', 1)
    source = source.replace('<link rel="stylesheet" href="teaching.css">', '<link rel="stylesheet" href="teaching.css"><link rel="stylesheet" href="integrated.css">')
    source = source.replace('<script defer src="teaching.js"></script>', '<script defer src="teaching.js"></script><script defer src="integrated.js"></script>')
    source = source.replace('<main id="lesson">', '<main class="integrated-workspace" id="workspace"><article id="lesson" class="integrated-reader">')
    source = source.replace('Every second counts.', 'Same time. Different distances.')
    source = source.replace('Every second counts · Itembank teaching prototype', 'Motion studies · Integrated candidate')
    source = source.replace('  <div class="lab-heading">', '''  <div class="integrated-tools" hidden><button id="focus-reading" type="button" aria-pressed="false">Focus reading</button><button id="open-note" type="button">Write a demo note</button><details><summary>Arrange workspace</summary><label for="companion-width">Companion width</label><input id="companion-width" type="range" min="260" max="400" step="20" value="300"></details></div>
  <div class="integrated-passage"><p class="step-eyebrow">READ / THE RELATIONSHIP</p><p id="source-passage">For constant speed, distance equals speed multiplied by elapsed time. Mira moves at 3 metres per second; Noor moves at 5. Both share the same elapsed time. Noor adds 2 more metres each second, so the gap grows by 2 metres for each second that passes.</p><button id="append-passage" type="button" hidden>Append passage to demo note</button></div>
  <div class="lab-heading">''', 1)
    source = source.replace('</main>', '''</article><aside id="companion" class="integrated-companion" tabindex="0" aria-label="Source and private demo note"><section class="integrated-reference"><p class="step-eyebrow">SOURCE CONTEXT / R1</p><h2>A model of constant speed</h2><blockquote>Distance is speed multiplied by elapsed time.</blockquote><p>Original synthetic model. Both start together, travel in the same direction, and keep constant speed.</p><p class="micro">This preview is a design candidate. No course score, accepted note, or learning evidence is recorded.</p><a href="lesson.md">Read the plain Markdown explanation</a></section>'''+note+'''<button id="return-passage" type="button" hidden>Return to the passage</button><p class="micro">Demo notes use this browser only. Production source notes keep their existing journal and revision controls.</p></aside></main>''', 1)
    source = source.replace('Prototype T · Original synthetic material · No assessment session', 'Integrated candidate · Original synthetic material · No assessment session')
    for old, new in {
        'Same time. Different distances.': 'Two walkers, one clock.',
        'THE MOTION LAB': 'Motion studies',
        'READ / THE RELATIONSHIP': 'Constant speed',
        '02 / CONNECT THE DOTS': 'Worked explanation',
        '03 / TRY A NEW TIME': 'Another elapsed time',
        'Keep the idea.': 'My notes',
        'Same start. Different speeds.': 'Compare their distances',
        'Two walkers. One clock. Find out what makes the gap grow.': 'Compare the distances Mira and Noor cover in the same elapsed time.',
        'Carry the idea into a fresh example.': 'Use the same speeds with a different elapsed time.',
        'YOUR THINKING': 'Private note',
    }.items():
        source = source.replace(old, new)
    (HERE / 'index.html').write_text(source)
    for name in ('teaching.css', 'teaching.js', 'lesson.md'):
        text = (LANES / 'teaching' / name).read_text()
        if name == 'teaching.js':
            text = text.replace('itembank-synthetic-teaching-20260930-note', 'itembank-integrated-teaching-20260930-note')
        (HERE / name).write_text(text)
    inputs = {}
    for lane, names in {'visual': ['index.html', 'design.css'], 'teaching': ['index.html', 'teaching.css', 'teaching.js'], 'workspace': ['index.html', 'workspace.css', 'workspace.js']}.items():
        for name in names:
            path = LANES / lane / name
            inputs[str(path.relative_to(LANES))] = hashlib.sha256(path.read_bytes()).hexdigest()
    (HERE / 'lane-inputs.json').write_text(json.dumps(inputs, indent=2))
    print('Integrated demonstration composed from frozen lane inputs.')
