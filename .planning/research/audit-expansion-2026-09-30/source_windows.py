"""Retain pinned implementation windows for the actual mechanisms compared."""
from pathlib import Path
import hashlib
import json
import urllib.request

OUT = Path(__file__).resolve().parent
ANCHORS = {
 'marimo-team/marimo': {'marimo/_runtime/dataflow/graph.py':['class DirectedGraph','def register_cell','def disable_cell'], 'frontend/src/core/cells/runs.ts':['stale','status'], 'frontend/src/core/cells/session.ts':['export','execution']},
 'coleifer/huey': {'huey/storage.py':['class SqliteStorage','def dequeue'], 'huey/api.py':['def _execute','def _requeue_task']},
 'agronholm/apscheduler': {'src/apscheduler/schedulers/base.py':['def _process_jobs'], 'src/apscheduler/jobstores/sqlalchemy.py':['def _get_jobs','def update_job']},
 'docling-project/docling': {'docling/document_converter.py':['def convert','def _execute_pipeline'], 'pyproject.toml':['dependencies ='], 'docs/concepts/docling_document.md':['Provenance','provenance']},
 'jupyter/nbformat': {'nbformat/sign.py':['def check_signature','def check_cells','def sign'], 'nbformat/v4/nbformat.v4.schema.json':['"id"']},
 'laurent22/joplin': {'packages/lib/services/RevisionService.ts':['collectRevisions','revision'], 'packages/lib/models/Revision.ts':['applyTextPatch','applyDiff','createTextPatch']},
 'pytest-dev/pluggy': {'src/pluggy/_manager.py':['def check_pending','def _verify_hook','def load_setuptools_entrypoints']},
 'open-spaced-repetition/py-fsrs': {'fsrs/scheduler.py':['def review_card','def reschedule_card'], 'pyproject.toml':['dependencies =']},
 'simonw/sqlite-utils': {'sqlite_utils/db.py':['def enable_fts','def rebuild_fts'], 'pyproject.toml':['dependencies =']},
}

def main():
    pins = json.loads((OUT/'primary-sources.json').read_text())
    windows = []
    for project in pins:
        repo,sha = project['repo'],project['sha']
        for path,needles in ANCHORS[repo].items():
            url = 'https://raw.githubusercontent.com/'+repo+'/'+sha+'/'+path
            with urllib.request.urlopen(url,timeout=25) as r:
                raw = r.read()
            lines = raw.decode().splitlines()
            for needle in needles:
                matches = [i for i,line in enumerate(lines) if needle in line]
                # Multiple overloads are retained but huge repeated occurrence
                # sets are limited explicitly to their first two matches.
                for i in matches[:2]:
                    windows.append(dict(repo=repo,sha=sha,path=path,anchor=needle,
                                        matches=len(matches),line=i+1,sha256=hashlib.sha256(raw).hexdigest(),
                                        text='\n'.join(lines[max(0,i-2):i+65])))
    (OUT/'mechanism-windows.json').write_text(json.dumps(windows,indent=2)+'\n')
    print('Retained',len(windows),'pinned source windows')

if __name__ == '__main__':
    main()
