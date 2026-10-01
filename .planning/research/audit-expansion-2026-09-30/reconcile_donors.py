"""Check original donor IDs against the live compact CAP crosswalk."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DONORS = [
 ('OpenMAIC upstream','om','.planning/research/OPENMAIC-GAP-INVENTORY-2026-09-27.md'),
 ('OpenTutor upstream','ot','.planning/research/opentutor-2026-09-27/GAP-INVENTORY.md'),
 ('LearnHouse upstream','lh','.planning/research/LEARNHOUSE-GAP-INVENTORY-2026-09-27.md'),
 ('LiaScript upstream','lia','.planning/research/liascript-gap-inventory-2026-09-27.md'),
 ('OpenMAIC fork features','omf','.planning/research/openmaic-forks-2026-09-27/FEATURES.md'),
 ('LearnHouse fork features','lhf','.planning/research/learnhouse-forks-2026-09-27/FEATURES.md'),
 ('Open Notebook fork features','onf','.planning/research/open-notebook-2026-09-27/FORKS.md'),
 ('Open Notebook UI fork audit','onu','.planning/research/open-notebook-2026-09-27/UI-FORK-AUDIT.md'),
]

def main():
    inventory = (ROOT/'.planning/FEATURE-INVENTORY.md').read_text()
    result = []
    for label,prefix,path in DONORS:
        compact = next(l for l in inventory.splitlines() if l.startswith('| ['+label+']'))
        routes = {}
        for match in re.finditer(r'\b([A-Z]+-?[FU]?\d{1,2})(?:-([A-Z]+-?[FU]?\d{1,2}))?\s+(CAP-\d{2}(?:/CAP-\d{2})*)',compact):
            start,end,caps = match.groups()
            cap_ids = re.findall(r'CAP-\d{2}',caps)
            if end:
                letters = re.match(r'(.+?)(\d+)$',start)[1]
                first = int(re.search(r'\d+$',start)[0])
                last = int(re.search(r'\d+$',end)[0])
                width = len(re.search(r'\d+$',start)[0])
                for number in range(first,last+1):
                    routes[letters+str(number).zfill(width)] = cap_ids
            else:
                routes[start] = cap_ids
        if prefix == 'om':
            # The compact source explicitly names this duplicate and sequence.
            fork_line = next(l for l in inventory.splitlines() if l.startswith('| [OpenMAIC fork features]'))
            for i in range(1,52):
                # Resolve ranges through the same parser on a temporary local map.
                for f in fork_line.split(';'):
                    m = re.search(r'FF(\d{2})(?:-FF(\d{2}))?\s+(CAP-.*)',f)
                    if m and int(m[1]) <= i <= int(m[2] or m[1]):
                        routes['I%02d'%i] = re.findall(r'CAP-\d{2}',m[3])
            j = [20,24,19,19,19,19,18,25,6,19,27,9,26,20]
            for i,cap in enumerate(j,1):
                routes['J%02d'%i] = ['CAP-%02d'%cap]
        for n,line in enumerate((ROOT/path).read_text().splitlines(),1):
            if not line.startswith('|'):
                continue
            first_cell = line.split('|')[1].strip().strip('*` ')
            m = (re.search(r'(LF\d{2})\b',first_cell) if prefix == 'lhf' else
                 re.match(r'((?:ON-[FU]\d|[A-Z]{1,2}\d{2}))\b',first_cell))
            if not m:
                continue
            original = m[1]
            result.append(dict(id=prefix+':'+original,original_id=original,path=path,line=n,
                               caps=routes.get(original,[]),text=line,
                               duplicate_of=('omf:FF'+original[1:]) if prefix=='om' and original.startswith('I') else None))
    ids = [r['id'] for r in result]
    print({label:sum(r['id'].startswith(prefix+':') for r in result) for label,prefix,path in DONORS})
    assert len(set(ids)) == len(ids), 'Duplicate donor IDs within one source'
    assert len(ids) == 604, len(ids)
    missing = [r['id'] for r in result if not r['caps']]
    assert not missing, missing
    (OUT/'donor-crosswalk.json').write_text(json.dumps(result,indent=2)+'\n')
    index = {cap:[r['id'] for r in result if cap in r['caps']]
             for cap in sorted({cap for r in result for cap in r['caps']})}
    (OUT/'cap-donor-index.json').write_text(json.dumps(index,indent=2)+'\n')
    metadata = {'total':len(result),'mapped':len(result)-len(missing),'unresolved':missing,
                'mirror_records':sum(bool(r['duplicate_of']) for r in result),
                'inventory_sha256':hashlib.sha256(inventory.encode()).hexdigest(),
                'by_source':{label:sum(r['id'].startswith(prefix+':') for r in result) for label,prefix,path in DONORS}}
    (OUT/'donor-summary.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps(metadata,indent=2))

if __name__ == '__main__':
    main()
