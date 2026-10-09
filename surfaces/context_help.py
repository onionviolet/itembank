"""Disposable, cited source questions over admitted reading and note owners.

Help never writes accepted content, attempts, grades or response evidence.
Preview and request handles are process-local capabilities. Restart loses them
and never replays a provider call. Assessment help uses the runtime elsewhere.
"""
import copy
import hashlib
import ipaddress
import json
import os
import secrets
import threading
import time
import urllib.parse

import course
import identity
import journal
import model
import model_adapter
import notes
import reading
import reading_desk
from surfaces import presentation, research_context

_LOCK = threading.RLock()
_PREVIEWS = {}
_JOBS = {}
_MAX_HANDLES = 64
_TTL = 1800


class HelpError(ValueError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


def _digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def contract_ready():
    """An unavailable operation cannot be disguised as authoring or a hint."""
    operations = model_adapter._SCHEMA['$defs']['request']['properties']['operation']['enum']
    return 'source_question' in operations and 'context_request' in model_adapter._PAYLOAD_KEYS


def _destination(settings_data):
    profile, error = model_adapter.resolve_profile(settings_data or {})
    if error:
        return None, {'state': 'unavailable', 'code': error['code'],
                      'message': 'Choose an enabled model profile in Settings.'}
    transport = profile['transport']
    endpoint = profile.get('endpoint') or ''
    remote = True
    if transport == 'openai_compatible':
        parsed = urllib.parse.urlsplit(endpoint)
        host = parsed.hostname or ''
        try:
            remote = not ipaddress.ip_address(host).is_loopback
        except ValueError:
            remote = host.lower() != 'localhost'
        # Do not display an endpoint's user info, query or credentials.
        destination = parsed.scheme + '://' + (parsed.hostname or '')
        if parsed.port:
            destination += ':' + str(parsed.port)
        destination += parsed.path
    else:
        destination = 'Configured CLI (' + os.path.basename((profile.get('command') or ['provider'])[0]) + ')'
    return profile, {'state': 'ready', 'profile': profile['name'],
                     'transport': transport, 'model': profile.get('model') or '',
                     'destination': destination, 'remote': remote,
                     'message': 'Selected context leaves this machine.' if remote else
                     'Selected context goes to this configured loopback endpoint.'}


def _protected_source(base, read, source_id):
    """Reject known assessment registrations before opening source bytes."""
    registry = journal.read_registry(base)
    row = registry.get(source_id) or {}
    protected_paths = {record.get('path') for record in registry.values()
                       if record.get('kind') in ('bank', 'assessment')}
    if row.get('kind') != 'source' or row.get('path') in protected_paths:
        raise HelpError('help.assessment_withheld', 'Assessment-linked help uses the runtime Practice or Test route.')
    state = identity.rights_state(row.get('rights'), 'read')
    if state != 'granted':
        raise HelpError('help.rights_' + state, 'Source read right is %s. Review its rights before asking.' % state)
    if journal.object_state(base, source_id) != 'clean':
        raise HelpError('help.stale', 'The source bytes changed. Review the source revision before asking.')
    path = os.path.join(base, row.get('path') or '')
    if not research_context.discovery.inside_any_root(path, [base]):
        raise HelpError('help.source_unavailable', 'Source path leaves this course.')
    with open(path, encoding='utf-8') as stream:
        raw = stream.read(2 * 1024 * 1024 + 1)
    if len(raw) > 2 * 1024 * 1024 or model.parse_bank(raw):
        raise HelpError('help.assessment_withheld', 'Assessment content is withheld. Use runtime Practice or Test help.')
    return row


def _admit(base, body, settings_data):
    allowed = {'expected_fingerprint', 'question', 'source', 'reading',
               'selection', 'note_ids', 'notes_fingerprint'}
    if not isinstance(body, dict) or set(body) - allowed:
        raise HelpError('help.assessment_withheld', 'Only a pure source question is supported here. Assessment linkage is withheld.')
    question = body.get('question')
    if not isinstance(question, str) or not question.strip() or len(question) > 2000:
        raise HelpError('help.question_invalid', 'Enter a source question of 1 to 2000 characters.')
    read, admitted = research_context._info(base)
    if body.get('expected_fingerprint') != read['fingerprint']:
        raise HelpError('help.stale', 'The course changed. Refresh and review the exact passage again.')
    source, task = body.get('source'), body.get('reading')
    if bool(source) == bool(task):
        raise HelpError('help.selection_invalid', 'Choose one source passage or one current reading occurrence.')
    return_href = '/course/' + urllib.parse.quote(os.path.basename(os.path.realpath(base)), safe='') + '/research'
    if task:
        if not isinstance(task, dict) or set(task) != {'occurrence_id', 'revision_id'}:
            raise HelpError('help.selection_invalid', 'Choose one current reading occurrence and revision.')
        read, occurrence = reading._current(base, dict(task, expected_fingerprint=read['fingerprint']))
        ref = occurrence['source_ref']
        row = _protected_source(base, read, ref['source_object_id'])
        span = course.validate_reading_source(base, ref)
        source = {'source_id': ref['source_object_id'], 'fingerprint': ref['source_fingerprint'],
                  'locator_id': ref['locator']}
        text = span['verbatim']
        return_href = '/course/%s/reading/%s/%s#source-content' % (
            urllib.parse.quote(os.path.basename(os.path.realpath(base)), safe=''),
            urllib.parse.quote(task['occurrence_id'], safe=''), urllib.parse.quote(task['revision_id'], safe=''))
    else:
        if (not isinstance(source, dict) or set(source) != {'source_id', 'fingerprint', 'locator_id'} or
                source['source_id'] not in admitted):
            raise HelpError('help.selection_invalid', 'Choose an accepted source passage in this course.')
        row = _protected_source(base, read, source['source_id'])
        text = research_context._safe_source(base, source)['text']
        return_href += '?' + urllib.parse.urlencode(source) + '#research-exact-passage'
    profile, provider = _destination(settings_data)
    rights = row.get('rights')
    required = ['read', 'quote', 'transform'] + (['remote_process'] if provider.get('remote') else [])
    for operation in required:
        state = identity.rights_state(rights, operation)
        if state != 'granted':
            raise HelpError('help.rights_' + state, 'Source %s right is %s. Review its rights before asking.' % (operation, state))
    selected = body.get('selection')
    if selected is not None:
        if not isinstance(selected, dict) or set(selected) != {'start', 'end', 'quote'}:
            raise HelpError('help.selection_invalid', 'Select exact words inside the admitted passage.')
        start, end, quote = selected['start'], selected['end'], selected['quote']
        if (type(start) is not int or type(end) is not int or not 0 <= start < end <= len(text) or
                not isinstance(quote, str) or quote != text[start:end]):
            raise HelpError('help.selection_invalid', 'The selected occurrence changed. Select it again.')
        text = text[start:end]
    if not text.strip() or len(text) > 12000:
        raise HelpError('help.context_large', 'Select a nonempty passage of at most 12000 characters.')
    ids = body.get('note_ids', [])
    if (not isinstance(ids, list) or len(ids) > 8 or
            any(not isinstance(value, str) for value in ids) or len(set(ids)) != len(ids)):
        raise HelpError('help.notes_invalid', 'Choose at most eight distinct private notes.')
    document = notes.read_note_document(reading_desk.note_root(base), read['object_id'])
    note_rows = [n for n in document['sidecar']['notes'] if n['status'] != 'deleted'] if document else []
    chosen = []
    if ids and (not document or document['fingerprint'] != body.get('notes_fingerprint')):
        raise HelpError('help.stale', 'The selected private notes changed. Review them again.')
    for note_id in ids:
        matches = [n for n in note_rows if n['note_id'] == note_id]
        if len(matches) != 1 or any(t['target_kind'] != 'source' for t in matches[0]['targets']):
            raise HelpError('help.notes_invalid', 'This note is missing or assessment-linked. Select a source note.')
        n = matches[0]
        if len(n['learner_wording']) > 4000:
            raise HelpError('help.context_large', 'Select a private note below 4000 characters.')
        chosen.append({'citation_id': 'N%d' % (len(chosen) + 1), 'note_id': note_id, 'wording': n['learner_wording']})
    payload = {'schema_version': 1, 'course_object_id': read['object_id'], 'question': question,
               'source_spans': [dict(source, citation_id='S1', text=text)],
               'learner_notes': chosen, 'attempt': 1}
    if len(json.dumps(payload, ensure_ascii=False).encode()) > 24576:
        raise HelpError('help.context_large', 'Choose a smaller passage and fewer notes.')
    return {'payload': payload, 'provider': provider, 'profile_pin': _digest(profile),
            'return_href': return_href, 'excluded_notes': len(note_rows) - len(chosen),
            'selection': copy.deepcopy(selected)}


def _prune():
    now = time.monotonic()
    for key, value in list(_PREVIEWS.items()):
        if now - value['created'] > _TTL:
            del _PREVIEWS[key]
    for key, value in list(_JOBS.items()):
        if value['done'].is_set() and now - value['created'] > _TTL:
            del _JOBS[key]
    if len(_PREVIEWS) + len(_JOBS) >= _MAX_HANDLES:
        raise HelpError('help.busy', 'Too many open previews. Close old help requests or restart this local workspace.')


def preview(base, body, settings_data):
    with journal._journal_lock(base):
        admitted = _admit(base, body, settings_data)
    handle = secrets.token_urlsafe(24)
    with _LOCK:
        _prune()
        _PREVIEWS[(os.path.realpath(base), handle)] = dict(admitted, body=copy.deepcopy(body),
            created=time.monotonic(), used=None)
    return dict(state='preview', preview_id=handle, contract_ready=contract_ready(),
                **{key: copy.deepcopy(admitted[key]) for key in ('provider', 'return_href', 'excluded_notes', 'selection')},
                **copy.deepcopy(admitted['payload']),
                next_action='Review the exact inclusion and destination, then explicitly ask once.')


def validate_candidate(candidate, payload):
    """Citation admission checks exact selected bytes; support is still advisory."""
    if (not isinstance(candidate, dict) or set(candidate) != {'schema_version', 'answer', 'citations', 'uncertainty'} or
            type(candidate['schema_version']) is not int or candidate['schema_version'] != 1 or not isinstance(candidate['answer'], str) or
            not candidate['answer'].strip() or len(candidate['answer'].encode('utf-8')) > 8192 or
            not isinstance(candidate['uncertainty'], str) or len(candidate['uncertainty'].encode('utf-8')) > 2048 or
            not isinstance(candidate['citations'], list) or not 1 <= len(candidate['citations']) <= 16):
        raise HelpError('help.candidate_invalid', 'The provider did not return the cited advisory format. No answer is displayed.')
    if len(json.dumps(candidate, ensure_ascii=False).encode('utf-8')) > 16384:
        raise HelpError('help.candidate_invalid', 'The cited output exceeds the bounded advisory format. No answer is displayed.')
    texts = {span['citation_id']: span['text'] for span in payload['source_spans']}
    texts.update({note['citation_id']: note['wording'] for note in payload['learner_notes']})
    source_ids = {span['citation_id'] for span in payload['source_spans']}
    source_cited = False
    for citation in candidate['citations']:
        if (not isinstance(citation, dict) or set(citation) != {'citation_id', 'quote'} or
                not isinstance(citation['citation_id'], str) or citation['citation_id'] not in texts or
                not isinstance(citation['quote'], str) or not citation['quote'].strip() or
                len(citation['quote']) > 2000 or citation['quote'] not in texts[citation['citation_id']]):
            raise HelpError('help.citation_invalid', 'A citation is outside the exact included context. No answer is displayed.')
        source_cited = source_cited or citation['citation_id'] in source_ids
    if not source_cited:
        raise HelpError('help.citation_invalid', 'The answer must cite the selected source. Private notes alone are not source support.')
    return copy.deepcopy(candidate)


def _failure(error, return_href=None):
    return {'state': 'unavailable', 'code': getattr(error, 'code', 'help.unavailable'),
            'message': str(error), 'return_href': return_href,
            'next_action': 'Retain your question. Review the source, notes and provider before making a new preview.'}


def start(base, body, settings_data):
    if (not isinstance(body, dict) or set(body) != {'preview_id', 'confirm'} or body['confirm'] is not True or
            not isinstance(body['preview_id'], str) or not 1 <= len(body['preview_id']) <= 128):
        raise HelpError('help.confirm_required', 'Review the exact preview and explicitly confirm this one provider request.')
    key = (os.path.realpath(base), body['preview_id'])
    with _LOCK:
        saved = _PREVIEWS.get(key)
        if not saved or time.monotonic() - saved['created'] > _TTL:
            raise HelpError('help.preview_unavailable', 'This preview expired or the local process restarted. Review a new preview; nothing was replayed.')
        if saved['used']:
            return status(base, {'request_id': saved['used']}, settings_data)
        if not contract_ready():
            raise HelpError('help.contract_unavailable', 'Source-question provider support is awaiting its accepted operation contract.')
        if saved['provider']['state'] != 'ready':
            raise HelpError('help.provider_off', 'Enable a configured model profile, then review a new preview.')
        with journal._journal_lock(base):
            current = _admit(base, saved['body'], settings_data)
        if _digest(current) != _digest({k: saved[k] for k in current}):
            raise HelpError('help.stale', 'The included context or destination changed. Review a new preview before sending.')
        _prune()
        if any(k[0] == key[0] and not value['done'].is_set() for k, value in _JOBS.items()):
            raise HelpError('help.busy', 'Finish or cancel the current source question first.')
        request_id = secrets.token_urlsafe(24)
        job = dict(created=time.monotonic(), cancel=threading.Event(), done=threading.Event(),
                   result=None, saved=saved)
        _JOBS[(key[0], request_id)] = job
        saved['used'] = request_id
    def run():
        result = None
        try:
            request = model_adapter.request_from_operation('source_question', 'help-' + request_id,
                saved['provider']['profile'], context_request=saved['payload'])
            result = model_adapter.invoke(request, settings_data, cancel=job['cancel'])
            if job['cancel'].is_set():
                result = {'state': 'canceled', 'message': 'Local waiting ended. A late result is discarded; provider completion may be unknown.'}
            elif result.get('status') != 'ok':
                error = result.get('error') or {}
                result = {'state': 'unavailable', 'code': error.get('code', 'help.provider_unavailable'),
                          'message': 'The configured provider returned no help. Review its status before retrying.'}
            else:
                candidate = validate_candidate(result.get('candidate'), saved['payload'])
                with journal._journal_lock(base):
                    current = _admit(base, saved['body'], settings_data)
                if _digest(current) != _digest({k: saved[k] for k in current}):
                    raise HelpError('help.stale', 'The context changed while waiting. The late answer is withheld.')
                result = {'state': 'answered', 'candidate': candidate,
                          'provider': saved['provider'], 'source_spans': saved['payload']['source_spans'],
                          'selection': saved['selection'],
                          'message': 'Generated advisory help. Citations match the selected bytes; review the explanation.'}
        except (HelpError, ValueError, OSError, journal.JournalError, course.CourseError) as error:
            result = _failure(error)
        except Exception:
            result = _failure(HelpError('help.unavailable', 'The request ended without usable help. No automatic retry will run.'))
        finally:
            with _LOCK:
                if job['cancel'].is_set():
                    result = {'state': 'canceled', 'message': 'Local waiting ended. Late help is discarded; provider completion may be unknown.'}
                job['result'] = dict(result, request_id=request_id, return_href=saved['return_href'])
                job['done'].set()
    threading.Thread(target=run, name='itembank-source-help', daemon=True).start()
    return {'state': 'running', 'request_id': request_id, 'return_href': saved['return_href'],
            'message': 'Waiting for this one source question. You can cancel local waiting.'}


def status(base, body, settings_data):
    if (not isinstance(body, dict) or set(body) != {'request_id'} or not isinstance(body['request_id'], str) or
            not 1 <= len(body['request_id']) <= 128):
        raise HelpError('help.request_invalid', 'Choose one owned request.')
    with _LOCK:
        job = _JOBS.get((os.path.realpath(base), body['request_id']))
        if not job:
            return {'state': 'unavailable', 'code': 'help.request_unowned',
                    'message': 'This request is no longer owned by the local process. Its outcome is unknown; nothing was replayed.'}
        if job['cancel'].is_set():
            return {'state': 'canceled', 'request_id': body['request_id'],
                    'return_href': job['saved']['return_href'], 'message': 'Local waiting canceled. Late help is discarded.'}
        result = copy.deepcopy(job['result']) if job['done'].is_set() else {
            'state': 'running', 'request_id': body['request_id'], 'return_href': job['saved']['return_href'],
            'message': 'Still waiting for this request. Refresh or cancel local waiting.'}
    if result['state'] == 'answered':
        try:
            with journal._journal_lock(base):
                current = _admit(base, job['saved']['body'], settings_data)
            if _digest(current) != _digest({k: job['saved'][k] for k in current}):
                raise HelpError('help.stale', 'The source, notes or provider changed. Previous help is withheld.')
        except (ValueError, OSError, journal.JournalError, course.CourseError) as error:
            return dict(_failure(error, job['saved']['return_href']), request_id=body['request_id'])
    return result


def cancel(base, body, settings_data):
    result = status(base, body, settings_data)
    if result.get('code') == 'help.request_unowned':
        return result
    with _LOCK:
        job = _JOBS.get((os.path.realpath(base), body['request_id']))
        if job:
            job['cancel'].set()
    return dict(result, state='canceled', candidate=None, message='Local waiting canceled. Late help is discarded; no automatic retry runs.')


def apply(base, action, body, settings_data):
    if action not in ('preview', 'start', 'status', 'cancel'):
        raise HelpError('help.operation_invalid', 'Choose preview, start, status or cancel.')
    return globals()[action](base, body, settings_data)


def form_apply(base, fields, settings_data):
    """Script-free controls use the same exact preview and owned request APIs."""
    one = research_context._one
    action = one(fields, 'operation')
    permitted = {'choose_source': {'source'},
                 'preview': {'source', 'locator', 'question', 'note_id', 'notes_fingerprint', 'expected_fingerprint'},
                 'start': {'preview_id', 'confirm'}, 'status': {'request_id'}, 'cancel': {'request_id'}}
    if action not in permitted or set(fields) - permitted[action] - {'operation'}:
        raise HelpError('help.form_invalid', 'Unsupported help fields. Retain your question and review the selection.')
    if action == 'choose_source':
        token = json.loads(one(fields, 'source'))
        research_context.locator_choices(base, token)
        return {'state': 'source_selected', 'source': token}
    if action == 'preview':
        token = json.loads(one(fields, 'source'))
        return preview(base, {'expected_fingerprint': one(fields, 'expected_fingerprint'),
            'source': dict(token, locator_id=one(fields, 'locator')), 'question': one(fields, 'question'),
            'note_ids': fields.get('note_id', []), 'notes_fingerprint': one(fields, 'notes_fingerprint') or None}, settings_data)
    body = {'preview_id': one(fields, 'preview_id'), 'confirm': one(fields, 'confirm') == 'yes'} if action == 'start' else {
        'request_id': one(fields, 'request_id')}
    return apply(base, action, body, settings_data)


CSS = '''
.context-help{margin-block:24px;padding:20px;border:1px solid var(--line);border-radius:12px;min-width:0}
.context-help label{display:block;margin-block:12px;overflow-wrap:anywhere}.context-help input:not([type=checkbox]),.context-help select,.context-help textarea{max-width:100%;width:100%;box-sizing:border-box}
.context-help select{white-space:normal}.context-help pre,.context-help p,.context-help code{white-space:pre-wrap;overflow-wrap:anywhere;max-width:100%}
.context-help button,.context-help summary{min-height:44px}.context-help button{margin:4px 8px 4px 0}.context-help textarea{min-height:100px}
.context-help [hidden]{display:none!important}.context-help fieldset{min-width:0}.context-help .help-answer{white-space:pre-wrap}
'''


def panel(base, result=None, retained=None, settings_data=None, course_id=None):
    esc = presentation.esc
    read, _admitted = research_context._info(base)
    cid = course_id or read['object_id']
    url = '/course/' + urllib.parse.quote(cid, safe='') + '/help'
    retained = retained or {}
    result = result or {}
    registry = journal.read_registry(base)
    document = notes.read_note_document(reading_desk.note_root(base), read['object_id'])
    def hidden(name, value):
        return '<input type="hidden" name="%s" value="%s">' % (name, esc(value))
    def form(action, body, label):
        return '<form method="post" action="%s">%s%s<button>%s</button></form>' % (
            esc(url), hidden('operation', action), body, esc(label))
    options, tokens = [], []
    for source in read['doc']['sources']:
        sid = source['source_object_id']
        token = {'source_id': sid, 'fingerprint': (registry.get(sid) or {}).get('fingerprint')}
        tokens.append(token)
        options.append('<option value="%s">%s</option>' % (esc(json.dumps(token)), esc(source.get('title') or sid)))
    chosen = result.get('source')
    try:
        chosen = chosen or (json.loads(research_context._one(retained, 'source')) if retained.get('source') else None)
    except ValueError:
        chosen = None
    if result.get('source_spans'):
        chosen = {key: result['source_spans'][0][key] for key in ('source_id', 'fingerprint')}
    chosen = chosen or (tokens[0] if tokens else None)
    out = ['<style>' + CSS + '</style><div class="context-help"><h2>Ask about a source passage</h2><p>Generated advisory help cites the exact selected source. It creates no accepted content, attempt, grade or response evidence. Assessment-linked help uses the runtime Practice or Test route.</p>']
    if result.get('message'):
        out.append('<p role="status">%s</p>' % esc(result['message']))
    out.append(form('choose_source', '<label>Source <select name="source" required>%s</select></label>' % ''.join(options), 'Choose source passages'))
    if chosen:
        try:
            choices = research_context.locator_choices(base, chosen)
            picker = '<label>Exact passage <select name="locator" required>%s</select></label>' % ''.join(
                '<option value="%s"%s>%s</option>' % (esc(row['ref']['locator_id']),
                ' selected' if row['ref']['locator_id'] == research_context._one(retained, 'locator') else '', esc(row['label'])) for row in choices)
            body = hidden('source', json.dumps(chosen)) + hidden('expected_fingerprint', read['fingerprint']) + picker
            body += '<label>Your source question <textarea name="question" maxlength="2000" required>%s</textarea></label>' % esc(
                result.get('question') or research_context._one(retained, 'question'))
            body += hidden('notes_fingerprint', document['fingerprint'] if document else '')
            body += '<fieldset><legend>Private notes to include (optional)</legend><p>Unchecked notes stay excluded. Inclusion grants this one request access to the selected wording.</p>'
            for note in (document['sidecar']['notes'] if document else []):
                if note['status'] != 'deleted':
                    body += '<label><input type="checkbox" name="note_id" value="%s"%s> %s</label>' % (
                        esc(note['note_id']), ' checked' if note['note_id'] in retained.get('note_id', []) else '', esc(note['learner_wording'][:120]))
            body += '</fieldset>'
            out.append(form('preview', body, 'Preview exact inclusion and destination'))
        except (ValueError, OSError, journal.JournalError):
            out.append('<p role="status">Source unavailable, changed, denied or assessment-linked. Choose another source or inspect recovery.</p>')
    if result.get('state') == 'preview':
        provider = result['provider']
        out.append('<h3>Exact request preview</h3><p>Question: %s</p>' % esc(result['question']))
        for span in result['source_spans']:
            out.append('<p>Source citation %s, locator %s, accepted revision %s</p><pre>%s</pre>' % (
                esc(span['citation_id']), esc(span['locator_id']), esc(span['fingerprint']), esc(span['text'])))
        if result.get('selection'):
            out.append('<p>Selected occurrence: code-point range %d:%d within this admitted passage.</p>' % (
                result['selection']['start'], result['selection']['end']))
        for note in result['learner_notes']:
            out.append('<p>Private learner note %s (not source truth)</p><pre>%s</pre>' % (esc(note['citation_id']), esc(note['wording'])))
        out.append('<p>%d private notes excluded. Only this question and the source/note fields shown above form the operation payload.</p>' % result['excluded_notes'])
        out.append('<p>Destination: %s. Profile: %s. Model: %s. %s</p>' % (
            esc(provider.get('destination', 'Provider disabled')), esc(provider.get('profile', 'none')),
            esc(provider.get('model', 'none')), esc(provider['message'])))
        if result['contract_ready'] and provider['state'] == 'ready':
            out.append(form('start', hidden('preview_id', result['preview_id']) +
                '<label><input type="checkbox" name="confirm" value="yes" required> Send exactly this preview, including each selected private note, to this configured provider once</label>', 'Ask configured provider'))
        else:
            out.append('<p role="status">Provider help is unavailable until a profile and the source-question operation contract are enabled.</p>')
    if result.get('request_id'):
        body = hidden('request_id', result['request_id'])
        out.append(form('status', body, 'Refresh this request'))
        if result['state'] == 'running':
            out.append(form('cancel', body, 'Cancel local waiting'))
    candidate = result.get('candidate')
    if result.get('state') == 'answered' and candidate:
        out.append('<h3>Advisory answer</h3><p class="help-answer">%s</p><h4>Included citations</h4>' % esc(candidate['answer']))
        for span in result.get('source_spans', []):
            out.append('<p>%s: source %s, exact locator %s, accepted revision %s</p>' % (
                esc(span['citation_id']), esc(span['source_id']), esc(span['locator_id']), esc(span['fingerprint'])))
        for citation in candidate['citations']:
            out.append('<p>%s: %s</p>' % (esc(citation['citation_id']), esc(citation['quote'])))
        out.append('<p>Uncertainty: %s</p>' % esc(candidate['uncertainty']))
    if result.get('return_href'):
        out.append('<p><a href="%s">Return to the exact source task</a></p>' % esc(result['return_href']))
    out.append('</div>')
    return ''.join(out)


def reader_panel(view):
    esc = presentation.esc
    note_choices = ''.join('<label><input type="checkbox" name="help-note" value="%s"> %s</label>' % (
        esc(note['note_id']), esc(note['learner_wording'][:120]))
        for note in view['notes'] if note.get('status') != 'deleted' and note.get('note_id'))
    return '''<details id="reading-help" class="context-help"><summary>Ask about this source range</summary>
<p>Optional generated advisory help. Preview the exact selected words and private notes before asking your configured provider. Assessment help uses Practice or Test.</p>
<p id="help-selection-state">The whole assigned range is selected. You can select words in the passage, then choose Ask about selection.</p>
<button id="help-whole-range" type="button">Use whole assigned range</button><label for="help-question">Your source question</label><textarea id="help-question" maxlength="2000"></textarea>
<fieldset id="help-note-choices"><legend>Private notes to include (optional)</legend><p>Unchecked notes stay excluded. Inclusion grants this one request access to the selected wording.</p>%s</fieldset>
<button id="help-preview" type="button" disabled>Preview exact inclusion and destination</button><div id="help-preview-content" hidden></div>
<label id="help-consent-label" hidden><input id="help-consent" type="checkbox"> Send exactly this preview, including each selected private note, to this configured provider once</label>
<button id="help-send" type="button" hidden disabled>Ask configured provider</button><button id="help-cancel" type="button" hidden>Cancel local waiting</button>
<p id="help-state" role="status" aria-live="polite"></p><div id="help-answer" hidden></div><button id="help-return" type="button">Return to exact passage</button></details>''' % note_choices


READER_SCRIPT = r'''
// Help is an advisory source question, never a scoring or acceptance surface.
const helpKey=continuityKey+':help';let helpSelection=null,helpPreview=null,helpRequest=null,helpEpoch=0,helpRestored=false,helpReturn=null;
const helpBox=$('#reading-help');
function helpBusy(busy){$('#help-question').readOnly=busy;$('#help-whole-range').disabled=busy;$('#reading-help-selection').disabled=busy;$('#help-preview').disabled=busy||!view||view.content===null||!!view.note_error;document.querySelectorAll('[name=help-note]').forEach(n=>n.disabled=busy);}
function helpSave(){try{sessionStorage.setItem(helpKey,JSON.stringify({source:sourceFingerprint(),question:$('#help-question').value,selection:helpSelection,preview:helpPreview,request:helpRequest,return:helpReturn,notes:Array.from(document.querySelectorAll('[name=help-note]:checked')).map(n=>n.value)}));}catch(e){$('#help-state').textContent='Local help recovery is unavailable. Copy your question before leaving.';}}
function helpClear(){helpEpoch++;helpPreview=null;$('#help-send').hidden=true;$('#help-consent-label').hidden=true;$('#help-consent').checked=false;$('#help-preview-content').hidden=true;$('#help-answer').hidden=true;helpSave();}
function helpRememberReturn(){if(!helpReturn)helpReturn=passageSnapshot();}
function helpSelect(){const selected=window.getSelection();if(!view||view.content===null||!selected||selected.rangeCount!==1||!readingSource.contains(selected.anchorNode)||!readingSource.contains(selected.focusNode)||!selected.toString().trim()){$('#reading-tools-state').textContent='Select words inside the source passage, then choose Ask about selection.';return;}const range=selected.getRangeAt(0),prefix=range.cloneRange();prefix.selectNodeContents(readingSource);prefix.setEnd(range.startContainer,range.startOffset);const start=Array.from(prefix.toString()).length,quote=range.toString();helpSelection={start,end:start+Array.from(quote).length,quote};helpReturn=null;helpRememberReturn();dismissReadingTools();helpClear();helpBox.open=true;$('#help-selection-state').textContent='Selected occurrence at character range '+helpSelection.start+':'+helpSelection.end+': '+quote;$('#help-question').focus();helpSave();}
async function helpApi(action,body){const response=await fetch('/api/course/context-help-'+action,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({course_id:ctx.course_id,...body})});let result;try{result=await response.json();}catch(e){throw Error('Help is unavailable. Retain your question and review the source or provider.');}if(!response.ok)throw Error(result.message||result.error?.message||'Request refused. Retain your question and review the exact preview.');return result;}
function helpText(root,tag,text){const node=document.createElement(tag);node.textContent=text;root.append(node);return node;}
function helpShowPreview(result){const root=$('#help-preview-content');root.replaceChildren();helpText(root,'h3','Exact request preview');helpText(root,'p','Question: '+result.question);for(const span of result.source_spans){helpText(root,'p','Source '+span.citation_id+' · '+span.locator_id+' · accepted revision '+span.fingerprint);helpText(root,'pre',span.text);}for(const note of result.learner_notes){helpText(root,'p','Private learner note '+note.citation_id+' (not source truth)');helpText(root,'pre',note.wording);}helpText(root,'p',result.excluded_notes+' private notes excluded. Only this question and the source/note fields shown above form the operation payload.');helpText(root,'p','Destination: '+(result.provider.destination||'Provider disabled')+'. Profile: '+(result.provider.profile||'none')+'. Model: '+(result.provider.model||'none')+'. '+result.provider.message);root.hidden=false;helpPreview=result.preview_id;const ready=result.contract_ready&&result.provider.state==='ready';$('#help-send').hidden=!ready;$('#help-consent-label').hidden=!ready;$('#help-send').disabled=true;$('#help-state').textContent=ready?'Review the exact inclusion and destination before sending.':'Provider help is unavailable until a profile and the source-question operation contract are enabled.';helpSave();}
function helpShowResult(result){helpBusy(result.state==='running');$('#help-state').textContent=result.message||result.next_action||result.state;$('#help-cancel').hidden=result.state!=='running';$('#help-answer').hidden=true;if(result.state==='answered'){const root=$('#help-answer');root.replaceChildren();helpText(root,'h3','Advisory answer');helpText(root,'p',result.candidate.answer).className='help-answer';helpText(root,'h4','Included citations');for(const citation of result.candidate.citations)helpText(root,'p',citation.citation_id+': '+citation.quote);helpText(root,'p','Uncertainty: '+result.candidate.uncertainty);root.hidden=false;}helpSave();}
async function helpPoll(epoch){if(!helpRequest)return;try{const result=await helpApi('status',{request_id:helpRequest});if(epoch!==helpEpoch)return;helpShowResult(result);if(result.state==='running')setTimeout(()=>helpPoll(epoch),1500);}catch(e){if(epoch===helpEpoch)$('#help-state').textContent=e.message;}}
function helpReady(){if(!helpBox)return;$('#help-preview').disabled=!view||view.content===null||!!view.note_error;if(helpRestored)return;helpRestored=true;let saved;try{saved=JSON.parse(sessionStorage.getItem(helpKey)||'null');}catch(e){return;}if(!saved)return;if(typeof saved.question==='string')$('#help-question').value=saved.question;if(!sourceFingerprint()||saved.source!==sourceFingerprint()){$('#help-state').textContent='The source changed or is unavailable. Your question is kept; select and preview the current passage again.';return;}helpSelection=saved.selection||null;helpPreview=saved.preview||null;helpRequest=saved.request||null;helpReturn=saved.return||null;for(const n of document.querySelectorAll('[name=help-note]'))n.checked=(saved.notes||[]).includes(n.value);if(helpSelection)$('#help-selection-state').textContent='Recovered selected occurrence at character range '+helpSelection.start+':'+helpSelection.end+': '+helpSelection.quote;if(helpRequest){helpBox.open=true;helpPoll(helpEpoch);}else if(helpPreview){helpBox.open=true;$('#help-state').textContent='Review a fresh exact preview before sending after reload.';helpPreview=null;}}
$('#reading-help-selection').onclick=helpSelect;
$('#help-whole-range').onclick=()=>{helpSelection=null;helpRememberReturn();helpClear();$('#help-selection-state').textContent='The whole assigned range is selected.';};
$('#help-question').oninput=helpClear;document.querySelectorAll('[name=help-note]').forEach(n=>n.onchange=helpClear);
$('#help-consent').onchange=()=>{$('#help-send').disabled=!$('#help-consent').checked||!helpPreview;};
$('#help-preview').onclick=async()=>{if(helpRequest){$('#help-state').textContent='Cancel or finish this request before previewing another.';const result=await helpApi('status',{request_id:helpRequest}).catch(()=>null);if(!result||result.state==='running')return;helpRequest=null;}const epoch=++helpEpoch;helpPreview=null;$('#help-send').hidden=true;$('#help-consent-label').hidden=true;$('#help-consent').checked=false;$('#help-answer').hidden=true;helpRememberReturn();try{const result=await helpApi('preview',{expected_fingerprint:ctx.expected_fingerprint,reading:{occurrence_id:ctx.occurrence_id,revision_id:ctx.revision_id},question:$('#help-question').value,selection:helpSelection,note_ids:Array.from(document.querySelectorAll('[name=help-note]:checked')).map(n=>n.value),notes_fingerprint:view.notes_fingerprint});if(epoch!==helpEpoch)return;helpShowPreview(result);}catch(e){if(epoch===helpEpoch)$('#help-state').textContent=e.message;}};
$('#help-send').onclick=async()=>{if(!helpPreview||!$('#help-consent').checked)return;const epoch=++helpEpoch;helpBusy(true);$('#help-send').disabled=true;try{const result=await helpApi('start',{preview_id:helpPreview,confirm:true});if(epoch!==helpEpoch)return;helpRequest=result.request_id;helpPreview=null;$('#help-send').hidden=true;$('#help-consent-label').hidden=true;helpShowResult(result);if(result.state==='running')helpPoll(epoch);}catch(e){if(epoch===helpEpoch){helpBusy(false);$('#help-state').textContent=e.message;}}};
$('#help-cancel').onclick=async()=>{if(!helpRequest)return;const request=helpRequest,epoch=++helpEpoch;$('#help-answer').hidden=true;$('#help-cancel').hidden=true;try{const result=await helpApi('cancel',{request_id:request});if(epoch!==helpEpoch)return;helpRequest=null;helpShowResult(result);}catch(e){if(epoch===helpEpoch)$('#help-state').textContent=e.message;}helpSave();};
$('#help-return').onclick=()=>{if(!restorePassagePosition(helpReturn))return;if(helpSelection&&readingSource.firstChild?.nodeType===Node.TEXT_NODE){const text=Array.from(readingSource.textContent),range=document.createRange();if(helpSelection.end<=text.length){range.setStart(readingSource.firstChild,text.slice(0,helpSelection.start).join('').length);range.setEnd(readingSource.firstChild,text.slice(0,helpSelection.end).join('').length);const selected=window.getSelection();selected.removeAllRanges();selected.addRange(range);}}};
window.addEventListener('pagehide',helpSave);
'''
