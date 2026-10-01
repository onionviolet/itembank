"""Apply deliberately reviewed route overrides to named historical findings."""
from pathlib import Path
import json
import re

OUT = Path(__file__).resolve().parent
OPPORTUNITIES = [
 ('F1',[4,13,15,27],'exact task return delivered at bounded source scope; explainer-state policy remains'),
 ('F2',[7,14,15],'private notes exist; reviewed contrast-practice chain remains'),
 ('F3',[7,8,25],'note doors/transport exist; distinct authored note-mode projection remains'),
 ('F4',[13,26],'transfer purpose exists; changed-demand subject review remains'),
 ('F5',[16,26],'resume separate; bounded time-budget stop policy remains'),
 ('O6',[6,10,15,27],'exact passages exist; comparison/scoped glossary task remains'),
 ('O7',[14,16,26],'confidence event field exists; capture/calibration equivalence remains'),
 ('O8',[6,7,15],'A1 search tracer, privacy/admission and exact task return remain'),
 ('O9',[17,24],'clean restore and newer C merged-copy slices; named package losses remain'),
 ('O10',[1,2,3,5,23],'native proposal lifecycle passes; instructional sequence fidelity remains'),
 ('O11',[4,14,16,26],'new composition remains prototype; revision recap is distinct from due work'),
]
MF = {
 1:[10,15,27],2:[10,13,22],3:[6,10,23],4:[10,13,26],5:[11,27],6:[6,25,27],
 7:[10,12,13],8:[10,13,15,26],9:[6,10,27],10:[7,11,27],11:[7,25],
 12:[7,11],13:[7,24],14:[3,23,25],15:[3,23],16:[2,3,7],
 17:[10,23,25],18:[9,15,27],
}
MF_REMAINDER = {
 1:'native authored glossary/disclosure owners exist; exact safe term across input modes needs representative review',
 2:'bounded two-MC stages are source-delivered; evolving case/P5 stage semantics and static disclosure remain',
 3:'source/rights/readiness owners exist; jurisdiction/date/conflicting protocol fixture and bounded revision review remain',
 4:'semantic example and transfer purpose exist; faded-step authorship plus independently changed demand needs subject review',
 5:'typed simulator/static cases stay prototype; numeric controls and scientifically valid equivalent task required',
 6:'source/glossary scope exists; actual mass/slope collision and linear formula-sheet export task remains',
 7:'execution checker exists with isolation limits; predict-before-execute and derived-output/static-trace task remains',
 8:'runtime hint release exists; bounded misconception branch and unavailable tutor fallback needs authored fixture',
 9:'exact source occurrences exist; conflicting histories with stacked cited comparison needs task evidence',
 10:'timeline visuals exist; disputed date precision and editable note/export semantics need fixture',
 11:'note persistence/projections exist; Cornell cue-note-summary authorship and outside-app recall remain',
 12:'objective graph exists; learner concept-map edge labels/identity and static adjacency stay distinct',
 13:'source-note anchors exist; arbitrary annotation move/edit/delete orphan recovery not inferred from quote notes',
 14:'bounded preview/diff/undo exists; protected keyed/objective/claim transformations need semantic comparison',
 15:'legacy audit skill and revision journal exist; one bounded warning insertion needs actual legacy audit/provenance gate',
 16:'source lesson drafting exists; source-extracted notes and guided lesson must demonstrate different teaching jobs',
 17:'semantic lesson roles exist; domain-specific severity/uncertainty authorability not certified by a shared card style',
 18:'native glossary/source return has bounded source proof; long quotation at 400 percent zoom and physical controls remain',
}
F = {1:[13],2:[13,22],3:[13,22],4:[12],5:[19,22],6:[9,13],7:[12,13],8:[11,12],9:[13,22],10:[11,26]}

def main():
    records = [json.loads(l) for l in (OUT/'records.jsonl').read_text().splitlines()]
    curated = []
    def select(label,path,pattern,caps,remainder,section=False):
        matches = [r for r in records if r['path'].endswith(path) and re.search(pattern,r['section'] if section else r['text'])]
        assert matches, (label,path,pattern)
        r = matches[0]
        curated.append(dict(label=label,record=r['id'],path=r['path'],line=r['lines'][0],
                            caps=['CAP-%02d'%n for n in caps],remainder=remainder,
                            evidence='CURRENT-EVIDENCE.md; READ-ME limits apply',
                            duplicate='named overlap, not an independently new product gap'))
    for code,caps,remainder in OPPORTUNITIES:
        select('Sep06-'+code,'2026-09-06-feature-opportunity-audit.md',r'\b'+code+r':',caps,remainder,True)
    for n,caps in MF.items():
        select('Atlas-MF-%02d'%n,'06-feature-style-atlas.md',r'^\| MF-%02d \|'%n,caps,
               MF_REMAINDER[n])
    for n in range(1,6):
        select('Sep19-U%d'%n,'ui-detail-review-2026-09-19.md',r'\bU%d:'%n,[4,10,27] if n==1 else [4,27],
               ['temporary-reset vs detour preservation decision','later native quiz/source return proof supersedes sampled old defect',
                'sampled phone placement passed; full human reflow gate remains','held-feedback course detour proof remains',
                'source-change/storage and focus/human overlap gates remain'][n-1],True)
    for n,caps in F.items():
        select('Question-F%d'%n,'question-types-2026-09-25/BACKLOG.md',r'^\| F%d \|'%n,caps,
               'use live backlog bounded source/prototype/backburner distinction; domains/P3/P5 need their named gates')
    for name,pattern,caps in [('grounding','normalized_with_map',[6,15]),('selection authority','_verified_selection',[6,15,24]),
                              ('retry','withGenerationRetry',[5,18,24]),('outline','generateSceneOutlinesFromRequirements',[2,3])]:
        select('Reuse-'+name,'competition-2026-09-08/REUSE-AUDIT.md',r'^\|.*'+pattern,caps,
               'older exact source pin retained; A1/A2 native reuse first, direct-copy/license test still open')
    for section,caps in [('2. Certainty-based',[14,16,26]),('3. Canvas outcome',[14,16]),
                          ('4. The question',[13,26]),('5. Open-licensed',[6,23])]:
        select('Sep05-'+section.split('.')[0],'2026-09-05-open-source-absorption.md',re.escape(section),caps,
               'historical opportunity retained; confidence/generator/corpus promotion needs actual task and rights',True)
    (OUT/'curated-findings.json').write_text(json.dumps(curated,indent=2)+'\n')
    rows=['# Reviewed named-finding crosswalk','',
          'This is the deliberately reviewed subset of the mechanical census. It is not exhaustive semantic deduplication. The remaining blocks keep their explicit inferred routes or unresolved status in CROSSWALK.md. Source line numbers are tied to manifest.json.', '',
          '| Named finding | Stable census record | Existing route | Actual retained remainder |',
          '| --- | --- | --- | --- |']
    rows += ['| %s | %s (%s:%s) | %s | %s |'%(r['label'],r['record'],r['path'],r['line'],', '.join(r['caps']),r['remainder']) for r in curated]
    (OUT/'CURATED-CROSSWALK.md').write_text('\n'.join(rows)+'\n')
    print('Deliberately reviewed named findings:',len(curated))

if __name__ == '__main__':
    main()
