#!/usr/bin/env python3
"""Structural ordering public/native workflow and daemon recovery, synthetic only."""
import argparse
import html
import json
from pathlib import Path
import re
import runpy
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import model
import runtime
from surfaces import quiz_page


def authored_text():
    def item(number, distractor=False):
        ids = ['start', 'left', 'right'] + (['spare'] if distractor else [])
        declaration = json.dumps(dict(version=1, blocks=ids, required=ids[:3],
                                      dependencies=[['start', 'left'], ['start', 'right']]))
        steps = '\n'.join('STEP) '+ident+' | '+label for ident, label in
                          zip(ids, ['Initialize', 'Independent task', 'Independent task', 'Unneeded task']))
        return f'''Q{number}. Arrange initialization before the two independent tasks.{' Leave the unneeded task unused.' if distractor else ''}
[TYPE: build]
[OBJECTIVE: synthetic:ordering.{number}]
[ORDERING: {declaration}]
{steps}
WHY BEST: Initialization supplies both independent tasks.
KEY DISCRIMINATOR: The independent tasks have no relative dependency.
DISTRACTOR ANALYSIS:
- An unneeded task would be correct only if the instructions required it.
TRAP: Treating identical labels as identical blocks.
CONFIDENCE: high

'''
    return '# Synthetic ordering workflow\n\n' + item(1) + item(2, True)


def public_checks():
    questions = model.parse_bank(authored_text())
    errors, _ = model.lint(questions)
    assert not errors, errors
    for q in questions:
        public = runtime.public_item(q)
        assert public['ordering']['version'] == 1 and public['ordering']['revision'] == model.content_fingerprint(q)
        assert 'required' not in public['ordering'] and 'dependencies' not in public['ordering']
        native = quiz_page._form_controls(public, {'step_0':['start'], 'step_2':['left']})
        assert 'data-ordering-signature' in native and 'Independent task (left)' in native
        assert 'value="start" selected' in native and 'value="left" selected' in native
        assert runtime.score_response(q, ['start','left','right']) is True
        assert runtime.score_response(q, ['start','right','left']) is True
        assert runtime.score_response(q, ['left','start','right']) is False
        held=dict(action='hold',score=False,ordering_diagnostic=dict(version=1,category='missing_required'))
        rendered=quiz_page.baseline_for(dict(session_id='s',item=public),{},'/answer',dict(submit='token'),flash=held)
        assert 'A required block is missing' in rendered
        assert 'Ordering response' in rendered and 'Leave unused blocks in the source area' in rendered
        assert 'Select every step' not in rendered
        held['action']='defer_feedback'
        silent=quiz_page.baseline_for(dict(session_id='s',item=public),{},'/answer',dict(submit='token'),flash=held)
        assert 'data-ordering-diagnostic' not in silent
    for mode in ('exam', 'diagnostic'):
        event=dict(mode=mode,session_id='synthetic',score=True,verdict=True,
                   explain={'ordering':questions[0]['ordering']})
        active=dict(mode=mode,status='active')
        feedback=runtime.evidence_feedback(event,active)
        assert 'score' not in feedback and 'explain' not in feedback and 'verdict' not in feedback
        assert not runtime.learner_evidence([event],{'synthetic':active})
    print('Ordering public/native: stable IDs, hidden constraints, duplicate labels, partial positions and alternative valid orders pass')


def journey(root, executable, browser_hold=False, mode='exam'):
    root.mkdir(exist_ok=True)
    (root/'ordering.md').write_text(authored_text())
    if browser_hold:
        matching_text = runpy.run_path(str(ROOT/'tests/matching_workflow_roundtrip.py'))['authored_text']()
        (root/'matching.md').write_text(matching_text)
    def launch():
        proc = subprocess.Popen([sys.executable,str(executable),'daemon',str(root),'--no-open','--port','0'],
                                stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        lines=[]
        threading.Thread(target=lambda:lines.extend(proc.stdout),daemon=True).start()
        for _ in range(100):
            match=re.search(r'http://127\.0\.0\.1:\d+/', ''.join(lines))
            if match: return proc, match.group(0)
            if proc.poll() is not None: break
            time.sleep(.1)
        proc.terminate()
        raise AssertionError('Daemon failed: '+''.join(lines))
    proc, base = launch()
    def get(path): return urllib.request.urlopen(urllib.parse.urljoin(base,path),timeout=10).read().decode()
    def post(page, values, override=None):
        token=re.search(r'name="form_token" value="([^"]+)"',page).group(1)
        action=html.unescape(re.search(r'<form method="post" action="([^"]+)"',page).group(1))
        data=[('step_'+str(i),v) for i,v in enumerate(values)]+[('action','submit'),('form_token',override or token)]
        req=urllib.request.Request(urllib.parse.urljoin(base,action),data=urllib.parse.urlencode(data).encode())
        try: return urllib.request.urlopen(req,timeout=10).read().decode(),200
        except urllib.error.HTTPError as exc: return exc.read().decode(),exc.code
    try:
        if browser_hold:
            print(json.dumps(dict(url=base+'quiz/ordering?mode=exam',root=str(root))),flush=True)
            input('Press Enter after disposable ordering browser checks: ')
            return
        page=get('quiz/ordering?mode='+mode)
        assert 'Independent task (left)' in page and 'Independent task (right)' in page
        if mode == 'practice':
            held,status=post(page,[])
            assert status==200 and 'A required block is missing' in held
            held,status=post(held,['left','start','right'])
            assert status==200 and 'A block appears before a prerequisite' in held
            receipt,status=post(held,['start','right','left'])
            assert status==200 and 'Correct' in receipt
            href=html.unescape(re.search(r'data-feedback-continue\s+href="([^"]+)"',receipt).group(1))
            page=get(href)
            held,status=post(page,['start','left','right','spare'])
            assert status==200 and 'An unneeded block is selected' in held
            receipt,status=post(held,['start','left','right'])
            assert status==200 and 'Correct' in receipt
            print('Ordering served practice: runtime-released missing block, dependency and distractor categories, exact retry and corrected alternative pass')
            return
        refused,status=post(page,['start','start'])
        assert status==400 and 'only once' in refused
        assert 'value="start" selected' in refused
        refused,status=post(page,['start','foreign'])
        assert status==400
        refused,status=post(page,['start','right','left'],'bad-token')
        assert status==403 and 'selected' in refused
        receipt,status=post(page,['start','right','left'])
        assert status==200 and 'Response recorded' in receipt
        desk=get('')
        assert 'Answered q1' in desk and 'Answered q1 (correct)' not in desk
        assert 'No activity yet' in get('activity')
        link=html.unescape(re.search(r'href="(/report\?session=[^"]+)"',desk).group(1))
        report=get(link)
        assert re.search(r'data-field="auto_correct"><div class="figure-value">([^<]+)',report).group(1) != '1'
        sid=urllib.parse.parse_qs(urllib.parse.urlsplit(link).query)['session'][0]
        proc.terminate(); proc.wait(timeout=10)
        proc,base=launch()
        assert 'In progress: 1 of 2 answered' in get('')
        page=get('quiz/ordering?mode='+mode+'&session='+sid)
        assert 'Unneeded task (spare)' in page
        receipt,status=post(page,['start','','left','right'])
        assert status==200 and 'Response recorded' in receipt
        events=[json.loads(line) for path in root.rglob('evidence.jsonl') for line in path.read_text().splitlines() if line.strip()]
        responses=[e for e in events if e.get('event_type')=='response' and e.get('bank')=='ordering.md']
        assert len(responses)==2 and all(e['score'] is True for e in responses), responses
        assert responses[0]['answer']==['start','right','left'], responses[0]
        assert responses[1]['answer']==['start','left','right'], responses[1]
        assert all(e.get('checker_version')==1 for e in responses), responses
        assert 'Answered q1 (correct)' in get('')
        print('Ordering served '+mode+': duplicate/foreign/token refusal, native blank compaction, hidden active verdicts, disk restart, alternative orders and raw stable IDs/checker version pass')
    finally:
        proc.terminate()
        try: proc.wait(timeout=10)
        except subprocess.TimeoutExpired: proc.kill(); proc.wait()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--runtime',type=Path,default=ROOT/'itembank.py')
    parser.add_argument('--browser-hold',action='store_true')
    args=parser.parse_args()
    public_checks()
    with tempfile.TemporaryDirectory(prefix='itembank-ordering-') as directory:
        root=Path(directory)
        if args.browser_hold:
            journey(root,args.runtime,True)
        else:
            journey(root/'exam',args.runtime)
            journey(root/'practice',args.runtime,mode='practice')


if __name__=='__main__': main()
