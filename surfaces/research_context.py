"""Native local source selection and quote notes over existing durable owners."""
import json
import os
import urllib.parse

import course
import discovery
import journal
import model
import notes
import reading_desk
import source_adapters
from surfaces import presentation

SCOPE_DIR = '_research'


def _roots(base):
    scope = os.path.join(base, SCOPE_DIR)
    private = reading_desk.note_root(base)
    if not discovery.inside_any_root(scope, [base]):
        raise ValueError('Research selection must stay inside this course.')
    return scope, private


def _info(base):
    read = course.read_course(base)
    if read['state'] != 'clean':
        raise ValueError('Repair the changed course record before using research context.')
    return read, {row['source_object_id'] for row in read['doc']['sources']}


def _safe_source(base, ref):
    """Admit course sources, never use this view to disclose an assessment."""
    _read, admitted = _info(base)
    if ref['source_id'] not in admitted:
        raise ValueError('Choose a source registered in this course.')
    result = source_adapters.resolve_locator(base, ref['source_id'], ref['locator_id'], ref['fingerprint'])
    if result['status'] != 'ok':
        raise ValueError(result.get('reason') or 'Source occurrence changed; retain the selection.')
    row = journal.read_registry(base).get(ref['source_id']) or {}
    path = os.path.join(base, row.get('path') or '')
    if not discovery.inside_any_root(path, [base]):
        raise ValueError('Source path is unavailable.')
    with open(path, encoding='utf-8') as stream:
        text = stream.read(2 * 1024 * 1024 + 1)
    if len(text) > 2 * 1024 * 1024 or model.parse_bank(text):
        raise ValueError('Assessment sources use the runtime practice or test route.')
    return result


def _one(fields, key, default=''):
    values = fields.get(key, [default])
    if len(values) != 1:
        raise ValueError('Submit one value for ' + key + '.')
    return values[0]


def search_selected(base, query):
    """Bounded literal retrieval over explicitly admitted local context only."""
    if (not isinstance(query, str) or not query.strip() or len(query) > 160 or
            any(ord(char) < 32 or ord(char) == 127 for char in query)):
        raise ValueError('Enter one literal query of 1 to 160 characters without control characters.')
    read, admitted = _info(base)
    scope_root, private = _roots(base)
    accepted = source_adapters.read_context_scope(scope_root, read['object_id'])
    if not accepted:
        raise ValueError('Save an explicit selection before searching.')
    scope = accepted['scope']
    if len(scope['sources']) + len(scope['note_ids']) > 128:
        raise ValueError('Select at most 128 passages and notes for one bounded search.')
    selected = {ref['source_id'] for ref in scope['sources']}
    common = {'query': query, 'egress': 'none', 'hits': [], 'truncated': False,
              'excluded_sources': len(admitted - selected),
              'selected_passages': len(scope['sources']), 'selected_notes': len(scope['note_ids'])}
    context = source_adapters.resolve_context_scope(base, scope, private)
    failures = list(context.get('failures') or [])
    if not failures:
        for ref in scope['sources']:
            try:
                _safe_source(base, ref)
            except (ValueError, OSError, journal.JournalError) as exc:
                failures.append({'kind': 'source', 'id': ref['source_id'],
                                 'locator_id': ref['locator_id'], 'state': 'unavailable',
                                 'reason': str(exc)})
    if failures:
        return dict(common, status='search_unavailable', failures=failures,
                    next_action='Review the selected revisions and rights. No snippets were disclosed.')
    passages = []
    for ref, resolved in zip(scope['sources'], context['sources']):
        passages.append((dict(ref, kind='source'), resolved['text']))
    for note in context['notes']:
        passages.append(({'kind': 'learner_note', 'note_id': note['note_id']}, note['wording']))
    hits = []
    for origin, text in passages:
        if len(text) > 2 * 1024 * 1024:
            return dict(common, status='search_unavailable', failures=[{'kind': origin['kind'], 'state': 'unsupported'}],
                        next_action='Select a smaller passage. No snippets were disclosed.')
        cursor = 0
        while True:
            start = text.find(query, cursor)
            if start < 0:
                break
            if len(hits) == 32:
                return dict(common, status='search', hits=hits, truncated=True, failures=[])
            end = start + len(query)
            hits.append(dict(origin, start=start, end=end,
                             excerpt=text[max(0, start - 80):min(len(text), end + 80)]))
            cursor = end
    return dict(common, status='search', hits=hits, failures=[])


def apply(base, fields):
    """Handle bounded native forms. A preview or cancel writes no durable state."""
    operation = _one(fields, 'operation')
    permitted = {
        'cancel': set(), 'preview': {'source', 'locator'},
        'link': {'source', 'locator', 'expected_notes_fingerprint', 'confirm'},
        'copy': {'source', 'locator', 'expected_notes_fingerprint', 'confirm'},
        'save_scope': {'reference', 'note_id', 'expected_notes_fingerprint', 'expected_scope_fingerprint', 'confirm'},
        'request_context': set(), 'search_context': {'query'}, 'undo_note': {'entry_id'},
    }
    if operation not in permitted or set(fields) - permitted[operation] - {'operation'}:
        raise ValueError('Unsupported research form fields.')
    if operation == 'cancel':
        return {'status': 'canceled'}
    if operation == 'search_context':
        return search_selected(base, _one(fields, 'query'))
    read, _admitted = _info(base)
    cid = read['object_id']
    scope_root, private = _roots(base)
    if operation in ('preview', 'link', 'copy'):
        token = json.loads(_one(fields, 'source'))
        if not isinstance(token, dict) or set(token) != {'source_id', 'fingerprint'}:
            raise ValueError('Choose the accepted source revision.')
        ref = dict(token, locator_id=_one(fields, 'locator').strip())
        resolved = _safe_source(base, ref)
        result = {'status': 'preview', 'citation': ref, 'passage': resolved}
        if operation != 'preview':
            transferred = notes.transfer_source_note(
                base, private, cid, ref, operation,
                _one(fields, 'expected_notes_fingerprint') or None,
                confirm=_one(fields, 'confirm') == 'yes')
            result.update(transferred)
        return result
    if operation == 'save_scope':
        refs = [json.loads(value) for value in fields.get('reference', [])]
        for ref in refs:
            _safe_source(base, ref)
        ids = fields.get('note_id', [])
        accepted = source_adapters.write_context_scope(
            scope_root, cid, refs, ids,
            (_one(fields, 'expected_notes_fingerprint') or None) if ids else None,
            _one(fields, 'expected_scope_fingerprint') or None, base, private,
            confirm=_one(fields, 'confirm') == 'yes')
        return {'status': 'saved' if 'scope' in accepted else accepted['status']}
    if operation == 'request_context':
        accepted = source_adapters.read_context_scope(scope_root, cid)
        if not accepted:
            raise ValueError('Save an explicit selection first.')
        for ref in accepted['scope']['sources']:
            _safe_source(base, ref)
        result = source_adapters.resolve_context_scope(base, accepted['scope'], private)
        if result['status'] != 'ok':
            raise ValueError('Selected content changed. Reload and review the selection.')
        return dict(result, status='context', excluded_sources=len(_admitted - {
            ref['source_id'] for ref in accepted['scope']['sources']}))
    if operation == 'undo_note':
        entry = _one(fields, 'entry_id')
        if not any(row.get('entry_id') == entry and row.get('state') == 'applied'
                   for row in journal.entries(private)):
            raise ValueError('Choose a recorded private-note change.')
        journal.undo(private, entry, 'human', 'research-notes')
        return {'status': 'undone'}
    raise ValueError('Choose a supported research action.')


def panel(base, result=None, retained=None):
    """Script-free preview, explicit inclusion, local context request and undo."""
    esc = presentation.esc
    read, admitted = _info(base)
    cid = read['object_id']
    scope_root, private = _roots(base)
    scope = source_adapters.read_context_scope(scope_root, cid)
    document = notes.read_note_document(private, cid)
    note_fp = document['fingerprint'] if document else ''
    url = '/course/%s/research' % urllib.parse.quote(cid, safe='')
    def hidden(name, value):
        return '<input type="hidden" name="%s" value="%s">' % (name, esc(value))
    def form(operation, body, label, confirmation=False):
        return ('<form method="post" action="%s">%s%s%s<button>%s</button></form>' % (
            url, hidden('operation', operation), body,
            '<label><input type="checkbox" name="confirm" value="yes" required> Confirm this local change</label>' if confirmation else '', esc(label)))
    out = ['<h2>Selected research context</h2><p>Exact source passages and private learner notes stay separate. Context requests here are local previews and send nothing to a model.</p>']
    if result:
        out.append('<p role="status">%s</p>' % esc(result['status']))
    registry = journal.read_registry(base)
    options = []
    for row in read['doc']['sources']:
        sid = row['source_object_id']
        record = registry.get(sid) or {}
        token = json.dumps({'source_id': sid, 'fingerprint': record.get('fingerprint')})
        options.append('<option value="%s"%s>%s</option>' % (esc(token),
            ' selected' if token == _one(retained or {}, 'source') else '', esc(row.get('title') or sid)))
    fields = ('<label>Source <select name="source" required>%s</select></label>'
              '<label>Exact locator ID <input name="locator" value="%s" required></label>' % (
                  ''.join(options), esc(_one(retained or {}, 'locator'))))
    out.append(form('preview', fields, 'Preview exact passage'))
    refs = list(scope['scope']['sources']) if scope else []
    if retained and _one(retained, 'operation') == 'save_scope':
        refs = []
        for value in retained.get('reference', []):
            try:
                ref = json.loads(value)
                if isinstance(ref, dict) and set(ref) == {'source_id', 'locator_id', 'fingerprint'}:
                    refs.append(ref)
            except ValueError:
                pass
    if result and result.get('citation'):
        ref = result['citation']
        passage = result['passage']
        out.append('<h3>Exact source preview</h3><pre>%s</pre><p>Source %s; accepted fingerprint %s; locator %s. Destination: this course\'s private _notes. A copied quote is a learner draft. Undo restores the previous note pair.</p>' % (
            esc(passage['text']), esc(ref['source_id']), esc(ref['fingerprint']), esc(ref['locator_id'])))
        rights = (registry.get(ref['source_id']) or {}).get('rights')
        out.append('<p>Current source rights: %s</p>' % esc(json.dumps(rights, sort_keys=True)))
        if ref not in refs:
            refs.append(ref)
        body = hidden('source', json.dumps({k: ref[k] for k in ('source_id', 'fingerprint')})) + hidden('locator', ref['locator_id']) + hidden('expected_notes_fingerprint', note_fp)
        out.append(form('link', body, 'Link occurrence in private notes', True))
        out.append(form('copy', body, 'Copy quote to private notes', True))
    selection = hidden('expected_scope_fingerprint', scope['fingerprint'] if scope else '') + hidden('expected_notes_fingerprint', note_fp)
    for ref in refs:
        selection += '<label><input type="checkbox" name="reference" value="%s" checked> Source %s, locator %s</label>' % (esc(json.dumps(ref)), esc(ref['source_id']), esc(ref['locator_id']))
    if document:
        selected_ids = (retained.get('note_id', []) if retained and _one(retained, 'operation') == 'save_scope'
                        else scope['scope']['note_ids'] if scope else [])
        for note in document['sidecar']['notes']:
            if note['status'] != 'deleted':
                selection += '<label><input type="checkbox" name="note_id" value="%s"%s> Learner note %s</label>' % (esc(note['note_id']), ' checked' if note['note_id'] in selected_ids else '', esc(note['note_id']))
    out.append('<h3>Explicit inclusion</h3><p>Unselected sources and notes are excluded. New inventory does not change this selection. Personal inclusion state is omitted from course export and named in its loss report.</p>')
    out.append(form('save_scope', selection, 'Save selected context', True))
    out.append(form('request_context', '', 'Request local selected context'))
    query = (result or {}).get('query') or _one(retained or {}, 'query')
    out.append('<h3>Search selected context</h3><p>Literal, case-sensitive search. Only saved passages and selected private notes are searched; no model or index is used.</p>')
    out.append(form('search_context', '<label>Query <input name="query" value="%s" maxlength="160" required></label>' % esc(query), 'Search selected context'))
    if result and result['status'] in ('search', 'search_unavailable'):
        out.append('<p>Selected passages: %d. Selected notes: %d. Excluded sources: %d. Egress: none.</p>' % (
            result['selected_passages'], result['selected_notes'], result['excluded_sources']))
        if result['status'] == 'search_unavailable':
            out.append('<p role="alert">%s</p><ul>%s</ul>' % (esc(result['next_action']), ''.join(
                '<li>%s: %s</li>' % (esc(row.get('kind')), esc(row.get('state'))) for row in result['failures'])))
        else:
            out.append('<p role="status">%d hits%s.</p>' % (len(result['hits']), '; more matches omitted after 32' if result['truncated'] else ''))
            for hit in result['hits']:
                label = ('Source %s, locator %s' % (hit['source_id'], hit['locator_id'])) if hit['kind'] == 'source' else 'Private learner note ' + hit['note_id']
                out.append('<section><h4>%s, code-point range %d:%d</h4><pre>%s</pre>' % (esc(label), hit['start'], hit['end'], esc(hit['excerpt'])))
                if hit['kind'] == 'source':
                    body = hidden('source', json.dumps({k: hit[k] for k in ('source_id', 'fingerprint')})) + hidden('locator', hit['locator_id'])
                    out.append(form('preview', body, 'Open exact source occurrence'))
                out.append('</section>')
    if result and result['status'] == 'context':
        out.append('<p>Excluded sources: %d. Egress: none. Purpose: local advisory context.</p>' % result['excluded_sources'])
        for passage in result['sources']:
            out.append('<h3>Source %s, locator %s</h3><pre>%s</pre>' % (esc(passage['source_id']), esc(passage['locator_id']), esc(passage['text'])))
        for note in result['notes']:
            out.append('<h3>Learner note %s</h3><pre>%s</pre>' % (esc(note['note_id']), esc(note['wording'])))
    entries = [entry for entry in journal.entries(private) if entry.get('state') == 'applied'] if os.path.isdir(private) else []
    if entries:
        out.append(form('undo_note', hidden('entry_id', entries[-1]['entry_id']), 'Undo latest private-note change'))
    out.append(form('cancel', '', 'Cancel without changes'))
    return ''.join(out)
