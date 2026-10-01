"""Adopt the user's character correction against the reviewed source revision."""
import difflib
import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TARGET = ROOT / 'surfaces/reading_desk.py'
EXPECTED = '0c2dd5eed12a04ff36994eb50f38fee513cb14377be384e838c9ac2ff789a98e'

if __name__ == '__main__':
    before = TARGET.read_bytes()
    assert hashlib.sha256(before).hexdigest() == EXPECTED, 'Changed base; inspect current ownership first'
    source = before.decode()
    changes = {
        'font-size:clamp(28px,3vw,40px);margin-block:16px 24px;font-weight:400': 'font-size:clamp(30px,3vw,42px);margin-block:16px 24px;font-weight:600',
        '.reading-column h2{font-family:var(--font-chrome);font-size:var(--text-xs);font-weight:600;letter-spacing:.08em;text-transform:uppercase}': '.reading-column h2{font-family:var(--font-paper);font-size:24px;font-weight:600;line-height:1.35}',
        'background:transparent;border:0;padding:0}': 'background:color-mix(in srgb,var(--source-bg) 45%,var(--paper));border:0;border-inline-start:3px solid var(--source-mark);padding:24px}',
        'border:1px solid var(--line);border-block-start:3px solid var(--note-mark);background:var(--card);padding:24px;position:sticky': 'border:0;border-inline-start:3px solid var(--note-mark);background:var(--note-bg);padding:24px;position:sticky',
        '.reading-notes h2{font-family:var(--font-chrome);font-size:var(--text-body)}': '.reading-notes h2{font-family:var(--font-paper);font-size:25px;font-weight:400;font-style:italic;line-height:1.3}',
        '.reading-toolbar button{background:transparent;color:var(--ink);border:1px solid var(--line);border-radius:var(--r-1)}': '.reading-toolbar button{background:transparent;color:var(--ink);border:0;border-bottom:1px solid transparent;border-radius:0}\n.reading-toolbar #reading-note-open{background:var(--note-bg);border-inline-start:2px solid var(--note-mark)}\n.reading-toolbar #reading-reference-open{background:var(--source-bg);border-inline-start:2px solid var(--source-mark)}',
        '.reading-toolbar button:hover{background:var(--card)}': '.reading-toolbar button:hover{background:var(--card);border-bottom-color:var(--line)}',
        '<h2>Assigned passage</h2>': '<h2>Source reading</h2>',
    }
    for old, new in changes.items():
        assert source.count(old) == 1, old
        source = source.replace(old, new, 1)
    after = source.encode()
    compile(after, str(TARGET), 'exec')
    (HERE / 'recovery/character-before.py.txt').write_bytes(before)
    (HERE / 'recovery/character.patch').write_text(''.join(difflib.unified_diff(before.decode().splitlines(True), source.splitlines(True), fromfile='a/surfaces/reading_desk.py', tofile='b/surfaces/reading_desk.py')))
    assert TARGET.read_bytes() == before, 'Concurrent change; refusing overwrite'
    temporary = TARGET.with_suffix('.py.character.tmp')
    temporary.write_bytes(after)
    os.replace(temporary, TARGET)
    (HERE / 'reading_desk.candidate.py.txt').write_bytes(after)
    (HERE / 'recovery/character-operation.json').write_text(json.dumps(dict(
        path='surfaces/reading_desk.py', before=json.loads((HERE / 'recovery/operation.json').read_text())['before'],
        adopted_from=EXPECTED, after=hashlib.sha256(after).hexdigest(), operation='user-character-correction'), indent=2))
    print(hashlib.sha256(after).hexdigest())
