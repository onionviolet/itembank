"""Read pinned public source and retain metadata plus bounded symbol excerpts.

No packages are installed or executed. Retry the same pinned manifest to
reinspect a snapshot; refreshing refs is an explicit separate research pass.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import datetime
import hashlib
import json
import re
import urllib.request

OUT = Path(__file__).resolve().parent
PROJECTS = {
 'marimo-team/marimo': ('main', ['LICENSE', 'pyproject.toml', 'marimo/_runtime/dataflow/graph.py', 'frontend/src/core/cells/types.ts', 'frontend/src/core/cells/runs.ts', 'frontend/src/core/cells/session.ts', 'docs/guides/exporting/static_html.md']),
 'coleifer/huey': ('master', ['LICENSE', 'setup.py', 'huey/storage.py', 'huey/api.py', 'huey/consumer.py']),
 'agronholm/apscheduler': ('3.11.0', ['LICENSE.txt', 'pyproject.toml', 'src/apscheduler/schedulers/base.py', 'src/apscheduler/jobstores/sqlalchemy.py']),
 'docling-project/docling': ('main', ['LICENSE', 'pyproject.toml', 'docling/document_converter.py', 'docs/concepts/docling_document.md']),
 'jupyter/nbformat': ('main', ['LICENSE', 'pyproject.toml', 'nbformat/sign.py', 'nbformat/v4/nbformat.v4.schema.json']),
 'laurent22/joplin': ('dev', ['LICENSE', 'packages/lib/services/RevisionService.ts', 'packages/lib/models/Revision.ts']),
 'pytest-dev/pluggy': ('main', ['LICENSE', 'pyproject.toml', 'src/pluggy/_manager.py']),
 'open-spaced-repetition/py-fsrs': ('main', ['LICENSE', 'pyproject.toml', 'fsrs/scheduler.py', 'fsrs/card.py']),
 'simonw/sqlite-utils': ('main', ['LICENSE', 'pyproject.toml', 'sqlite_utils/db.py']),
}
PATTERN = re.compile(r'^(?:class |def |    def |\s*(?:private |public |async )?\w*(?:collectRevision|createRevision|applyDiff|revision).*\()|retries|retry_delay|revok|cancel|dequeue|_process_jobs|misfire|coalesc|provenance|trust|cell_id|check_pending|is_enabled|create_fts|rebuild_fts|enable_fts|schedule_card|log_revi|dependencies\s*=|license\s*=', re.I)

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'itembank-read-only-research','Accept':'application/vnd.github+json'})
    with urllib.request.urlopen(req,timeout=25) as r:
        return r.read()

def inspect(item):
    repo,(ref,paths) = item
    try:
        saved = OUT/'primary-sources.json'
        previous = json.loads(saved.read_text()) if saved.exists() else []
        pin = next((p.get('sha') for p in previous if p['repo'] == repo), None)
        commit = json.loads(get('https://api.github.com/repos/'+repo+'/commits/'+(pin or ref)))
        sha = commit['sha']
        result = dict(repo=repo,requested_ref=ref,sha=sha,commit_date=commit['commit']['committer']['date'],
                      inspected_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=[])
        for path in paths:
            url = 'https://raw.githubusercontent.com/'+repo+'/'+sha+'/'+path
            row = dict(path=path,url='https://github.com/'+repo+'/blob/'+sha+'/'+path)
            try:
                raw = get(url)
                lines = raw.decode().splitlines()
                row.update(sha256=hashlib.sha256(raw).hexdigest(),lines=len(lines))
                if 'LICENSE' in path:
                    row['license_text'] = '\n'.join(lines)
                elif path.endswith(('toml','setup.py')):
                    row['manifest_text'] = '\n'.join(lines)
                else:
                    hits = [i for i,line in enumerate(lines) if PATTERN.search(line)]
                    selected = sorted(set(j for i in hits for j in range(max(0,i-2),min(len(lines),i+6))))
                    row['excerpts'] = [{'line':i+1,'text':lines[i]} for i in selected]
            except Exception as exc:
                row['error'] = str(exc)
            result['files'].append(row)
        return result
    except Exception as exc:
        return dict(repo=repo,error=str(exc))

def main():
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(inspect,PROJECTS.items()))
    (OUT/'primary-sources.json').write_text(json.dumps(results,indent=2)+'\n')
    for project in results:
        print(project['repo'],project.get('sha',project.get('error')),
              [(f['path'],f.get('error','ok')) for f in project.get('files',[])])

if __name__ == '__main__':
    main()
