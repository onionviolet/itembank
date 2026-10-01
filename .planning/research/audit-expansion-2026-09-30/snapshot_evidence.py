"""Tie only four scoped checks to source fingerprints in this shared checkout."""
from pathlib import Path
import hashlib
import json
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PATHS = ['surfaces/agent_operation.py','surfaces/discovery_cache.py','surfaces/research_context.py',
         'surfaces/course_ops.py','source_adapters.py','discovery.py','director.py','model_adapter.py',
         'extension_registry.py','retention.py','journal.py','course.py','notes.py','note_outputs.py',
         '.planning/FEATURE-INVENTORY.md','.planning/research/AUDIT-REMAINING-2026-09-30.md']
TESTS = ['tests/discovery_cache_roundtrip.py','tests/agent_operation_roundtrip.py',
         'tests/extension_registry_roundtrip.py','tests/a5_research_context_roundtrip.py']

def hashes():
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in PATHS+TESTS}

def main():
    before = hashes()
    results = []
    for test in TESTS:
        started = time.monotonic()
        p = subprocess.run(['python3',test],cwd=ROOT,capture_output=True,text=True,timeout=120)
        result = dict(command='python3 '+test,exit_code=p.returncode,seconds=round(time.monotonic()-started,3),
                      stdout=p.stdout,stderr=p.stderr)
        results.append(result)
    after = hashes()
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    snapshot = dict(head=head,before=before,after=after,changed_during_checks=[p for p in before if before[p]!=after[p]],tests=results)
    (OUT/'native-evidence.json').write_text(json.dumps(snapshot,indent=2)+'\n')
    caps = [line for line in (ROOT/'.planning/FEATURE-INVENTORY.md').read_text().splitlines() if line.startswith('| CAP-')]
    report = ['# Current source evidence and authority profiles','',
              'Snapshot HEAD: `'+head+'`. `native-evidence.json` retains before/after fingerprints and exact focused outputs. This is source evidence only. Installed, packaged, physical touch, screen-reader, human preference and learning efficacy were not tested.', '',
              '## Focused checks','',
              '| Command | Exit | Elapsed seconds |','| --- | --- | --- |']
    report += ['| `%s` | %d | %s |'%(r['command'],r['exit_code'],r['seconds']) for r in results]
    report += ['', 'Files changing during checks: '+(', '.join(snapshot['changed_during_checks']) or 'none among the fingerprinted paths')+'.', '',
               '## Current route profiles','',
               'These are the live owning inventory rows at the fingerprinted snapshot, attached to older records by route. They do not establish that every older feature in a CAP is implemented. Other CAP evidence is owner-reported, not rerun by A. Use PACKETS.md and CURATED-CROSSWALK.md for sampled current seams and explicit retained gaps.', '',
               '| ID | Job | Owning current statement | Retained gate |','| --- | --- | --- | --- |']
    report += caps
    report += ['', '## Symbol-first sampling limits','',
               'Sampled agent_operation.start/status/accept/undo, discovery-cache classification/scan, director checkpoint/replay/resume, research-context safe source and apply/panel, source-adapter contract and context resolution, extension-registry validation, retention objective replay, and daemon route searches. Large modules were not read whole. Course/workspace, evidence and runtime end-to-end delivery remains tied to the existing owners; no fresh whole-product acceptance is claimed.', '',
               '## Current shared work','',
               'C owns integration and has reported a preserving merged-copy restore seam. Its report and later source tests must be consulted live. A did not repeat restore, P3, P5, UI or broad gates. Reading-desk/vision/ledger dirty edits belong to other writers.']
    (OUT/'CURRENT-EVIDENCE.md').write_text('\n'.join(report)+'\n')
    print({r['command']:r['exit_code'] for r in results})
    print('Changed during checks:',snapshot['changed_during_checks'])

if __name__ == '__main__':
    main()
