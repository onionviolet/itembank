#!/usr/bin/env python3
"""Synthetic authored matching lifecycle, disclosure and real native POST journey."""
import argparse
import copy
import html
import json
from pathlib import Path
import re
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
import audit_writer
import authoring
import model
import runtime
import schema_validate
from surfaces import home, quiz_page, session


def authored_text():
    choices = [{"id":"a","text":"Token"},{"id":"b","text":"Token"},
               {"id":"spare","text":"Unused"}]
    def item(number, reuse, stem, keys):
        spec = json.dumps(dict(version=1, reuse=reuse, choices=choices))
        return f'''Q{number}. {stem}
[TYPE: dnd]
[OBJECTIVE: synthetic:matching.{number}]
[MATCHING: {spec}]
ITEM) first | Select token {keys[0]}. :: {keys[0]}
ITEM) second | Select token {keys[1]}. :: {keys[1]}
WHY BEST: The requested token identities determine the mapping.
KEY DISCRIMINATOR: A label can repeat while an identity stays distinct.
DISTRACTOR ANALYSIS:
- Spare would be correct only if explicitly requested.
TRAP: Treating repeated labels as the same choice.
CONFIDENCE: high

'''
    return '# Synthetic matching workflow\n\n' + item(1,'once','Match distinct requested tokens.', ['a','b']) + item(2,'unlimited','Reuse the requested token for both rows.', ['a','a'])


def contract_checks(text):
    qs = model.parse_bank(text)
    errors, _ = model.lint(qs)
    assert not errors, errors
    schema = json.loads((ROOT / 'schemas/item.schema.json').read_text())
    for q in qs:
        public = runtime.public_item(q)
        assert not schema_validate.validate(public, schema)
        assert all('cat' not in r for r in public['rows'])
        assert public['matching']['choices'][0]['text'] == public['matching']['choices'][1]['text']
        key = {r['id']:r['cat'] for r in q['rows']}
        assert runtime.score_response(q, key) is True
        assert runtime.score_response(q, dict(first='spare',second='b')) is False
        for invalid in ({}, {'first':'a'}, dict(first='a',second='foreign'), dict(first='a',second='b',extra='a')):
            assert runtime.matching_response_error(q, invalid)
            assert runtime.score_response(q, invalid) is False
        markup = quiz_page._form_controls(public, {})
        assert 'Token (a)' in markup and 'Token (b)' in markup
    assert runtime.matching_response_error(qs[0], dict(first='a',second='a'))
    assert runtime.matching_response_error(qs[1], dict(first='a',second='a')) is None
    for changes in (dict(version=2), dict(reuse='sometimes'), dict(choices=None), dict(choices=[{'id':'a','text':'x'}])):
        q = copy.deepcopy(qs[0]); q['matching'].update(changes)
        assert model.matching_spec_errors(q)
    for declaration in ('[MATCHING: {broken}]', '[MATCHING: ]',
                        '[MATCHING: {"version":1,"version":1}]'):
        malformed = re.sub(r'(?m)^\[MATCHING:.*$', declaration, text, count=1)
        errors, _ = model.lint(model.parse_bank(malformed))
        assert any(error.code == 'item.invalid_matching' for error in errors)
    q = copy.deepcopy(qs[0]); q['rows'][1]['id'] = 'first'
    assert model.matching_spec_errors(q)
    q = copy.deepcopy(qs[0]); q['rows'][1]['cat'] = 'a'
    assert model.matching_spec_errors(q)
    q = copy.deepcopy(qs[0]); q['matching']['choices'][0]['text'] = 'Changed'
    assert model.content_fingerprint(q) != model.content_fingerprint(qs[0])
    q = copy.deepcopy(qs[0]); q['rows'][0]['id'] = 'changed'
    assert model.content_fingerprint(q) != model.content_fingerprint(qs[0])
    legacy = next(q for q in model.parse_bank((ROOT/'fixtures/sample_bank.md').read_text()) if q['type']=='dnd')
    assert runtime.score_response(legacy, {str(i):r['cat'] for i,r in enumerate(legacy['rows'])}) is True
    for mode in ('exam','diagnostic'):
        event = dict(mode=mode,session_id='s',score=False,verdict=False,explain={'why':'secret'})
        assert 'score' not in runtime.evidence_feedback(event)
        active = dict(mode=mode,status='active')
        assert 'explain' not in runtime.evidence_feedback(event, active)
        closed = dict(mode=mode,status='complete')
        assert runtime.evidence_feedback(event,closed)['score'] is False
        assert not runtime.learner_evidence([event], {'s':active})
        assert runtime.learner_evidence([event], {'s':closed})
    print('Matching contract: stable IDs, duplicate labels, capacities, distractors, malformed specs, legacy semantics and fail-closed disclosure pass')


def author_checks(text, root):
    blocks = re.split(r'(?m)(?=^Q\d+\.)', text)[1:]
    citation = dict(source_id='synthetic',fingerprint='synthetic-v1',span_id='tokens')
    request = dict(schema_version=authoring.AUTHORING_SCHEMA_VERSION,
        objectives=['synthetic:matching.1','synthetic:matching.2'],count=2,
        item_types=['dnd'],citations=[citation],mode='draft_and_approve',retry_cap=1)
    response = dict(schema_version=authoring.AUTHORING_SCHEMA_VERSION,items=[
        dict(objective='synthetic:matching.'+str(i+1),type='dnd',citations=[citation],text=block)
        for i,block in enumerate(blocks)])
    bank = root/'author.md'; before='# Synthetic author target\n'; bank.write_text(before)
    state = root/'author-state'
    cfg = dict(target_path=str(bank),state_dir=str(state))
    report = authoring.run_authoring(request,lambda _:response,before,audit_writer.write_units,cfg)
    assert report['status']=='awaiting_approval', report
    assert bank.read_text()==before
    assert 'MATCHING' in report['proposal']['diff']
    cfg['approved_write_ids'] = report['pending_write_ids']
    accepted = authoring.run_authoring(request,lambda _:response,before,audit_writer.write_units,cfg)
    assert accepted['status']=='written', accepted
    assert len(model.parse_bank(bank.read_text()))==2
    print('Matching authoring: reviewed proposal, lint, diff, exact approval and transactional shadow write pass')


def practice_checks(text, root):
    root.mkdir()
    bank = root/'practice.md'; bank.write_text(text)
    sitting = root/'sitting.json'
    session.do_start(str(bank), dict(count=2, seed=0, objective='', selection_mode='exam'),
                     'practice', str(sitting), False)
    before = sitting.read_bytes()
    try:
        session.do_submit(str(sitting), json.dumps(dict(first='a',second='a')), None)
        raise AssertionError('Forbidden reuse was accepted')
    except SystemExit as exc:
        assert 'only once' in str(exc)
    assert sitting.read_bytes() == before
    wrong = session.do_submit(str(sitting), json.dumps(dict(first='spare',second='b')), None)
    assert wrong['score'] is False and wrong['action'] == 'hold', wrong
    right = session.do_submit(str(sitting), json.dumps(dict(first='a',second='b')), None)
    assert right['score'] is True and right['action'] == 'advance', right
    assert runtime.explain_payload(model.parse_bank(text)[0])['row_cats'] == dict(first='a',second='b')
    print('Matching practice: invalid entry leaves session intact; valid wrong answer holds, revision passes and runtime releases ID-based feedback')


def journey(text, root, executable, browser_hold=False):
    bank = root/'matching.md'; bank.write_text(text)
    command = [sys.executable,str(executable),'daemon',str(root),'--no-open','--port','0']
    def launch():
        proc = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        lines=[]; threading.Thread(target=lambda:lines.extend(proc.stdout),daemon=True).start()
        for _ in range(100):
            match = re.search(r'http://127\.0\.0\.1:\d+/', ''.join(lines))
            if match: return proc, match.group(0)
            if proc.poll() is not None: break
            time.sleep(.1)
        proc.terminate(); raise AssertionError('Serve failed: '+''.join(lines))
    proc,base=launch()
    def get(url): return urllib.request.urlopen(url,timeout=10).read().decode()
    def post(page, values, token_override=None):
        token = re.search(r'name="form_token" value="([^"]+)"',page).group(1)
        action = html.unescape(re.search(r'<form method="post" action="([^"]+)"',page).group(1))
        data = [('row_'+str(i),v) for i,v in enumerate(values)] + [('action','submit'),('form_token',token_override or token)]
        req=urllib.request.Request(urllib.parse.urljoin(base,action),data=urllib.parse.urlencode(data).encode())
        try: return urllib.request.urlopen(req,timeout=10).read().decode(),200
        except urllib.error.HTTPError as exc: return exc.read().decode(),exc.code
    try:
        if browser_hold:
            print(json.dumps(dict(url=base+'quiz/matching?mode=exam',root=str(root))),flush=True)
            input('Press Enter after disposable matching browser checks: '); return
        page=get(base+'quiz/matching?mode=exam')
        assert 'Token (a)' in page and 'Token (b)' in page
        rejected,status=post(page,['a','a'])
        assert status==400 and 'only once' in rejected, (status,rejected)
        assert 'selected' in rejected
        refused,status=post(page,['a','b'],'invalid')
        assert status==403 and 'selected' in refused
        receipt,status=post(page,['a','b'])
        assert status==200 and 'Response recorded' in receipt
        desk=get(base)
        assert 'Answered q1' in desk and 'Answered q1 (correct)' not in desk
        assert 'No activity yet' in get(base+'activity')
        link=html.unescape(re.search(r'href="(/report\?session=[^"]+)"',desk).group(1))
        report=get(urllib.parse.urljoin(base,link))
        assert re.search(r'data-field="auto_correct"><div class="figure-value">([^<]+)',report).group(1) != '1'
        assert 'Token (a)' not in report
        assert 'Match distinct requested tokens' not in get(base+'report')
        # Resume the exact recorded session after process restart.
        proc.terminate(); proc.wait(timeout=10)
        proc,base=launch()
        desk=get(base)
        assert 'In progress: 1 of 2 answered' in desk
        sid = urllib.parse.parse_qs(urllib.parse.urlsplit(link).query)['session'][0]
        page=get(base+'quiz/matching?mode=exam&session='+sid)
        assert 'Reuse the requested token' in page, page[:500]
        receipt,status=post(page,['a','a'])
        assert status==200 and 'Response recorded' in receipt
        events=[json.loads(line) for path in root.rglob('evidence.jsonl') for line in path.read_text().splitlines() if line.strip()]
        responses=[e for e in events if e.get('event_type')=='response' and e.get('bank')=='matching.md']
        assert len(responses)==2, responses
        assert all(e['score'] is True for e in responses)
        assert responses[0]['answer']==dict(first='a',second='b'), responses[0]
        assert responses[1]['answer']==dict(first='a',second='a'), responses[1]
        report=get(urllib.parse.urljoin(base,link))
        assert re.search(r'data-field="auto_correct"><div class="figure-value">([^<]+)',report).group(1) == '2'
        assert 'Answered q1 (correct)' in get(base)
        print('Matching served journey: invalid capacity/token refusal, revision, withheld cross-surface feedback, exact process restart, reusable response, released report and two raw events pass')
    finally:
        proc.terminate()
        try: proc.wait(timeout=10)
        except subprocess.TimeoutExpired: proc.kill(); proc.wait()


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--runtime',type=Path,default=ROOT/'itembank.py'); parser.add_argument('--browser-hold',action='store_true')
    args=parser.parse_args(); text=authored_text()
    with tempfile.TemporaryDirectory(prefix='itembank-matching-') as directory:
        root=Path(directory)
        contract_checks(text)
        if not args.browser_hold:
            author_checks(text,root)
            practice_checks(text,root/'practice-check')
        journey(text,root,args.runtime,args.browser_hold)

if __name__=='__main__': main()
