"""Verify snapshots, complete line accounting, unique IDs and exact totals."""
from pathlib import Path
import collections
import hashlib
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]

def main():
    manifest = json.loads((OUT/'manifest.json').read_text())
    records = [json.loads(line) for line in (OUT/'records.jsonl').read_text().splitlines()]
    excluded = json.loads((OUT/'exclusions.json').read_text())
    summary = json.loads((OUT/'summary.json').read_text())
    assert len({r['id'] for r in records}) == len(records)
    assert len(manifest) == summary['files']
    assert len(records) == summary['records']
    assert sum(bool(r['duplicate_of']) for r in records) == summary['exact_duplicate_records']
    assert dict(collections.Counter(r['routing'] for r in records)) == summary['routing']
    indexed = collections.defaultdict(set)
    for row in records+excluded:
        indexed[row['path']].update(range(row['lines'][0],row['lines'][1]+1))
    changed = []
    for item in manifest:
        raw = (ROOT/item['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != item['sha256']:
            changed.append(item['path'])
        assert set(range(1,len(raw.decode().splitlines())+1)) <= indexed[item['path']], item['path']
    assert not changed, ('Source snapshot changed; refresh or preserve dated evidence',changed)
    donors = json.loads((OUT/'donor-crosswalk.json').read_text())
    assert len(donors)==604 and all(r['caps'] for r in donors)
    assert len({r['id'] for r in donors}) == 604
    curated = json.loads((OUT/'curated-findings.json').read_text())
    ids = {r['id'] for r in records}
    assert all(r['record'] in ids for r in curated)
    own_prose = ['README.md','PACKETS.md','BACKEND-COMPARISON.md','CURRENT-EVIDENCE.md',
                 'CURATED-CROSSWALK.md','CROSSWALK.md']
    for name in own_prose:
        text = (OUT/name).read_text()
        assert '\u2014' not in text, name
        assert '/Users/' not in text, name
    print('PASS: %d files, %d accounted records, %d exact duplicates, %d named reviewed findings, 604 mapped donor IDs' %
          (len(manifest),len(records),summary['exact_duplicate_records'],len(curated)))

if __name__ == '__main__':
    main()
