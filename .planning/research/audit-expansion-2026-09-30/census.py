"""Reproduce a bounded historical Markdown record census, without learner files.

Run from the repository root. Routing is an explicit lexical proposal, never
delivery evidence. Every nonblank source line is either represented or listed
as structural exclusion. Original text is retained in JSONL for review.
"""
from pathlib import Path
import collections
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PATTERNS = [
    '.planning/research/phase-16/*.md',
    '.planning/research/*2026-09-05*.md',
    '.planning/research/*2026-09-06*.md',
    '.planning/research/*2026-09-08*.md',
    '.planning/research/*2026-09-09*.md',
    '.planning/research/*2026-09-12*.md',
    '.planning/research/*2026-09-18*.md',
    '.planning/research/competition-2026-09-08/*.md',
    '.planning/research/overhaul-2026-09-18/*.md',
    '.planning/research/source-to-reading/*2026-09-12*.md',
    '.planning/*AUDIT*2026-09-06.md',
    '.planning/*AUDIT*2026-09-08.md',
    '.planning/*AUDIT*2026-09-09.md',
    '.reasonix/*audit*2026-09-19.md',
    '.reasonix/*review*2026-09-19.md',
    '.reasonix/parity-implementation-handoff-2026-09-19.md',
    '.reasonix/quiz-audit-2026-09-19/browser-evidence.md',
    '.reasonix/parity-handoff-ui-supplement-20260919/*.md',
    'prototypes/ui-renewal-20260918/research/*.md',
    '.planning/research/opentutor-2026-09-27/FORKS.md',
    '.planning/research/opentutor-2026-09-27/UI-FORK-AUDIT.md',
    '.planning/research/learnhouse-forks-2026-09-27/UI-AUDIT.md',
    '.planning/research/open-notebook-2026-09-27/INTEGRATION.md',
    '.planning/research/question-types-2026-09-25/README.md',
    '.planning/research/question-types-2026-09-25/01-current-types.md',
    '.planning/research/question-types-2026-09-25/02-execution-math.md',
    '.planning/research/question-types-2026-09-25/03-reference-patterns.md',
    '.planning/research/question-types-2026-09-25/BACKLOG.md',
    '.planning/research/structured-question-presentation-audit-2026-09-15.md',
    '.planning/research/code-question-depth-audit-2026-09-16.md',
]
# A match proposes an existing job route, not equivalence of individual ideas.
ROUTES = {
 'CAP-01': r'first.use|onboard|course shelf|course creation|course entry|scaffold',
 'CAP-02': r'curriculum|objective (?:map|graph)|outline|treatment|blueprint',
 'CAP-03': r'author|edit(?:or|ing)|draft|accept(?:ed)? revision|transformation|legacy upgrade',
 'CAP-04': r'resume|detour|continuity|return (?:to|position)|navigation|workspace',
 'CAP-05': r'job|operation|retry|cancel|interrupt|worker|queue',
 'CAP-06': r'extract|retriev|index|search|discover|locator|source acquisition',
 'CAP-07': r'annotation|notebook|learner note|private note|confusion',
 'CAP-08': r'copy quote|transfer.*note|note.*transfer|cross.workspace',
 'CAP-09': r'image|media|caption|asset|illustration',
 'CAP-10': r'reveal|emphasis|callout|guided|worked example|prediction',
 'CAP-11': r'simulat|diagram|chart|visualization|concept map|timeline',
 'CAP-12': r'execut|sandbox|runnable|SQL|Parsons|notebook kernel',
 'CAP-13': r'inline check|embedded.*question|practice|retrieval practice',
 'CAP-14': r'retention|review queue|spaced|FSRS|remediat|feedback|confidence calibration',
 'CAP-15': r'tutor|grounding|chat|contextual help|grounded',
 'CAP-16': r'progress|denominator|time.budget|time.aware|briefing|Today|notification|schedule',
 'CAP-17': r'export|import|restore|package|interchange|portable',
 'CAP-18': r'provider|egress|local model|model adapter|cost|Ollama',
 'CAP-19': r'speech|audio|pronunciation|playback|bilingual|transcript',
 'CAP-20': r'collaborat|multi.user|sync|sharing|access control',
 'CAP-21': r'commercial|billing|institution|LMS|catalog|publication',
 'CAP-22': r'rubric|prose|reviewer|assignment|partial credit|marking',
 'CAP-23': r'audit|quality|readiness|fidelity|validation|lint',
 'CAP-24': r'recover|crash|conflict|stale|disk.full|atomic|failure|offline',
 'CAP-25': r'plugin|extension|macro|template|skill|registry',
 'CAP-26': r'strateg|personaliz|transfer challenge|recommend',
 'CAP-27': r'accessib|keyboard|screen.reader|reflow|responsive|contrast|theme|style|presentation',
}

def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()

def blocks(path):
    lines = path.read_text().splitlines()
    section = []
    pending = []
    start = None
    fenced = False
    for n, line in enumerate(lines + [''], 1):
        if fenced:
            if line.startswith('```'):
                fenced = False
            yield n, n, 'code', ' '.join(section), line
            continue
        heading = re.match(r'^(#{1,6})\s+(.+)', line)
        table_header = line.startswith('|') and n < len(lines) and re.match(r'^\s*\|?\s*:?-{3,}', lines[n])
        structural = not line.strip() or heading or table_header or re.match(r'^\s*\|?\s*:?-{3,}', line)
        fence = line.startswith('```')
        boundary = structural or fence or line.startswith('|') or re.match(r'^\s*(?:[-*+] |\d+\. )', line)
        if pending and boundary:
            yield start, n - 1, 'code' if fenced else 'block', ' '.join(section), '\n'.join(pending)
            pending, start = [], None
        if heading and not fenced:
            level = len(heading[1])
            section = section[:level-1] + [heading[2]]
        if fence:
            fenced = not fenced
        if structural or fence:
            yield n, n, 'structural', ' '.join(section), line
            continue
        if line.startswith('|'):
            yield n, n, 'table-row', ' '.join(section), line
        else:
            if start is None:
                start = n
            pending.append(line)

def main():
    paths = sorted(set(p for pattern in PATTERNS for p in ROOT.glob(pattern)))
    records, excluded, manifest = [], [], []
    seen = {}
    collisions = collections.Counter()
    for path in paths:
        rel = path.relative_to(ROOT).as_posix()
        raw = path.read_bytes()
        manifest.append({'path': rel, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
        for first, last, kind, section, text in blocks(path):
            if kind == 'structural' or kind == 'code':
                excluded.append({'path': rel, 'lines': [first,last], 'reason': kind})
                continue
            normalized = re.sub(r'\s+', ' ', text).strip()
            h = digest(normalized)
            key = digest(rel + '\n' + normalized)[:14]
            collisions[key] += 1
            rid = 'OA-' + key + (('-' + str(collisions[key])) if collisions[key] > 1 else '')
            caps = [cap for cap, regex in ROUTES.items() if re.search(regex, section+' '+text, re.I)]
            # Avoid meaningless many-route claims for long synthesis paragraphs.
            status = 'route-proposed' if 0 < len(caps) <= 6 else 'unresolved'
            duplicate = seen.get(h)
            seen.setdefault(h, rid)
            explicit = re.findall(r'\b(?:CAP-\d{2}|MF-\d{2}|IL-\d{8}-\d{2}|ON-[FU]\d|FF\d{2}|LF\d{2})\b', text)
            records.append(dict(id=rid,path=rel,lines=[first,last],section=section,text=text,
                                content_sha256=h,duplicate_of=duplicate,proposed_caps=caps,
                                routing=status,explicit_ids=sorted(set(explicit)),
                                evidence='CURRENT-EVIDENCE.md; profile is route-level, not record delivery',
                                delivery='not individually established'))
    counts = collections.Counter(r['routing'] for r in records)
    duplicates = sum(bool(r['duplicate_of']) for r in records)
    summary = dict(files=len(paths),records=len(records),exact_duplicate_records=duplicates,
                   unique_normalized_records=len(records)-duplicates,routing=dict(counts),
                   structural_or_code_exclusions=len(excluded),
                   scope_patterns=PATTERNS,head='see CURRENT-EVIDENCE.md')
    summary['by_source'] = {m['path']:{'records':sum(r['path']==m['path'] for r in records),
                                    'exact_duplicates':sum(r['path']==m['path'] and bool(r['duplicate_of']) for r in records),
                                    'unresolved':sum(r['path']==m['path'] and r['routing']=='unresolved' for r in records)} for m in manifest}
    for name,value in [('manifest.json',manifest),('summary.json',summary),('exclusions.json',excluded)]:
        (OUT/name).write_text(json.dumps(value,indent=2)+'\n')
    (OUT/'records.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in records))
    rows = ['# Older record crosswalk','',
            'Generated by census.py. Routes are explicit lexical proposals. Exact duplicates retain both IDs. Unresolved means ambiguous route, not rejected scope. Every row has original text and source fingerprints in records.jsonl and manifest.json. See README.md for census units and exclusions.', '',
            '| Stable record | Source and line | Original IDs | Proposed route | Reconciliation |',
            '| --- | --- | --- | --- | --- |']
    for r in records:
        src = r['path']+':'+str(r['lines'][0])
        state = ('exact duplicate of '+r['duplicate_of']) if r['duplicate_of'] else r['routing']
        rows.append('| %s | %s | %s | %s | %s |' % (r['id'],src,', '.join(r['explicit_ids']),', '.join(r['proposed_caps']),state))
    (OUT/'CROSSWALK.md').write_text('\n'.join(rows)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('by_source','scope_patterns')},indent=2))

if __name__ == '__main__':
    main()
