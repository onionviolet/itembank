"""Native local source selection and quote notes over existing durable owners."""
import json
import os
import urllib.parse
from array import array

import course
import discovery
import identity
import journal
import model
import notes
import reading_desk
import source_adapters
from surfaces import course_source_search, presentation

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
    # Reuse the reading authority's accepted sidecar check. A well-formed
    # edited locator must not redirect a duplicate quote to another occurrence.
    sidecar_path = source_adapters.sidecar_path_for(path)
    with open(sidecar_path, 'rb') as stream:
        sidecar_raw = stream.read(2 * 1024 * 1024 + 1)
    if len(sidecar_raw) > 2 * 1024 * 1024:
        raise ValueError('Source locator sidecar is too large.')
    course.validate_reading_source(base, {'source_object_id': ref['source_id'],
        'source_fingerprint': ref['fingerprint'], 'locator': ref['locator_id'],
        'range': {'span_id': result['span_id'], 'locator_id': ref['locator_id'],
                  'locator_sidecar_fingerprint': identity.object_fingerprint(sidecar_raw, 'source')}})
    return result


def _one(fields, key, default=''):
    values = fields.get(key, [default])
    if len(values) != 1:
        raise ValueError('Submit one value for ' + key + '.')
    return values[0]


def locator_choices(base, token):
    """Human-readable exact occurrences, without text-based duplicate lookup."""
    _read, admitted = _info(base)
    if (not isinstance(token, dict) or set(token) != {'source_id', 'fingerprint'} or
            token['source_id'] not in admitted):
        raise ValueError('Choose an accepted source in this course.')
    row = journal.read_registry(base).get(token['source_id']) or {}
    path = os.path.join(base, source_adapters.sidecar_path_for(row.get('path') or ''))
    if not discovery.inside_any_root(path, [base]):
        raise ValueError('Source locator path is unavailable.')
    with open(path, encoding='utf-8') as stream:
        sidecar = json.load(stream)
    choices = []
    for locator in sidecar.get('locators', []):
        if locator.get('span_id') is None:
            continue
        ref = dict(token, locator_id=locator['id'])
        resolved = _safe_source(base, ref)
        body = resolved['origin']
        position = ', '.join('%s %s' % (key.replace('_', ' '), value)
                             for key, value in body.items()
                             if isinstance(value, (str, int)) and key != 'kind')
        label = '%s: %s' % (position or locator['id'], ' '.join(resolved['text'].split())[:100])
        choices.append({'ref': ref, 'label': label})
        if len(choices) >= 256:
            break
    return choices


def _literal_ranges(text, query, match_case):
    """Keep Unicode case folding separate from original citation offsets."""
    if match_case:
        haystack, needle, origins = text, query, None
    else:
        pieces, origins = [], array('I')
        for index, char in enumerate(text):
            folded = char.casefold()
            pieces.append(folded)
            origins.extend([index] * len(folded))
        haystack, needle = ''.join(pieces), query.casefold()
    cursor = 0
    while True:
        found = haystack.find(needle, cursor)
        if found < 0:
            return
        stop = found + len(needle)
        start, end = (found, stop) if origins is None else (origins[found], origins[stop - 1] + 1)
        # A match may not select only half of an expanded character such as ß.
        if origins is None or text[start:end].casefold() == needle:
            yield start, end
            cursor = stop
        else:
            # An invalid partial expansion must not hide a later full match.
            cursor = found + 1


def search_selected(base, query, *, match_case=True, offset=0):
    """Bounded literal retrieval over explicitly admitted local context only."""
    if (not isinstance(query, str) or not query.strip() or len(query) > 160 or
            any(ord(char) < 32 or ord(char) == 127 for char in query)):
        raise ValueError('Enter one literal query of 1 to 160 characters without control characters.')
    if type(match_case) is not bool or type(offset) is not int or not 0 <= offset <= 4096:
        raise ValueError('Choose a valid search mode and a result offset from 0 to 4096.')
    read, admitted = _info(base)
    scope_root, private = _roots(base)
    accepted = source_adapters.read_context_scope(scope_root, read['object_id'])
    if not accepted:
        raise ValueError('Save an explicit selection before searching.')
    scope = accepted['scope']
    if len(scope['sources']) + len(scope['note_ids']) > 128:
        raise ValueError('Select at most 128 passages and notes for one bounded search.')
    selected = {ref['source_id'] for ref in scope['sources']}
    common = {'query': query, 'match_case': match_case, 'offset': offset,
              'egress': 'none', 'hits': [], 'truncated': False, 'next_offset': None,
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
    # Check every passage before returning even the first page of snippets.
    for origin, text in passages:
        if len(text) > 2 * 1024 * 1024:
            return dict(common, status='search_unavailable', failures=[{'kind': origin['kind'], 'state': 'unsupported'}],
                        next_action='Select a smaller passage. No snippets were disclosed.')
    skipped = 0
    for origin, text in passages:
        for start, end in _literal_ranges(text, query, match_case):
            if skipped < offset:
                skipped += 1
                continue
            if len(hits) == 32:
                return dict(common, status='search', hits=hits, truncated=True, failures=[],
                            next_offset=offset + 32 if offset + 32 <= 4096 else None)
            hits.append(dict(origin, start=start, end=end,
                             excerpt=text[max(0, start - 80):min(len(text), end + 80)]))
    return dict(common, status='search', hits=hits, failures=[])


def apply(base, fields):
    """Handle bounded native forms. A preview or cancel writes no durable state."""
    operation = _one(fields, 'operation')
    permitted = {
        'cancel': set(), 'choose_source': {'source'},
        'preview': {'source', 'locator', 'return_query', 'match_start', 'match_end',
                    'return_ignore_case', 'return_offset'},
        'link': {'source', 'locator', 'expected_notes_fingerprint', 'confirm'},
        'copy': {'source', 'locator', 'expected_notes_fingerprint', 'confirm'},
        'save_scope': {'reference', 'note_id', 'expected_notes_fingerprint', 'expected_scope_fingerprint', 'confirm'},
        'request_context': set(), 'search_context': {'query', 'ignore_case', 'offset'},
        'search_course_sources': {'query', 'ignore_case', 'offset', 'return_match'}, 'undo_note': {'entry_id'},
    }
    if operation not in permitted or set(fields) - permitted[operation] - {'operation'}:
        raise ValueError('Unsupported research form fields.')
    if operation == 'cancel':
        return {'status': 'canceled'}
    if operation in ('search_context', 'search_course_sources'):
        ignore_case = _one(fields, 'ignore_case')
        if ignore_case not in ('', 'yes'):
            raise ValueError('Choose whether to ignore capitalization.')
        try:
            offset = int(_one(fields, 'offset', '0'))
        except ValueError:
            raise ValueError('Choose a valid result page.') from None
        search = course_source_search.search if operation == 'search_course_sources' else search_selected
        returned = _one(fields, 'return_match') if operation == 'search_course_sources' else ''
        if returned:
            course_source_search.validate_return_match(returned)
        result = search(base, _one(fields, 'query'), match_case=ignore_case != 'yes', offset=offset)
        if returned:
            result['return_match'] = returned
        return result
    read, _admitted = _info(base)
    cid = read['object_id']
    scope_root, private = _roots(base)
    if operation == 'choose_source':
        token = json.loads(_one(fields, 'source'))
        return {'status': 'source_selected', 'source': token,
                'choices': locator_choices(base, token)}
    if operation in ('preview', 'link', 'copy'):
        token = json.loads(_one(fields, 'source'))
        if not isinstance(token, dict) or set(token) != {'source_id', 'fingerprint'}:
            raise ValueError('Choose the accepted source revision.')
        ref = dict(token, locator_id=_one(fields, 'locator').strip())
        resolved = _safe_source(base, ref)
        result = {'status': 'preview', 'citation': ref, 'passage': resolved}
        if operation == 'preview':
            result = course_source_search.admit_match(base, result, fields)
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
        return ('<form class="context-search research-context-form" method="post" action="%s">%s%s%s<button>%s</button></form>' % (
            url, hidden('operation', operation), body,
            '<label><input type="checkbox" name="confirm" value="yes" required> Confirm this local change</label>' if confirmation else '', esc(label)))
    out = ['<style>.research-source-preview{white-space:pre-wrap;overflow-wrap:anywhere;max-width:100%;min-width:0;line-height:1.6}'
        '.research-source-preview #course-source-match{scroll-margin-block:96px}'
        '.course-search-return{margin-block:16px}'
        '.context-search.research-context-form{max-width:100%;margin-block:16px}'
        '.research-context-form label{min-height:44px}'
        '.research-context-form select{display:block;box-sizing:border-box;width:100%;max-width:100%;min-width:0;min-height:44px;font:inherit;padding:8px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--ink)}</style>',
        '<h2>Selected research context</h2><p>Exact source passages and private learner notes stay separate. Context requests here are local previews and send nothing to a model.</p>']
    if result:
        out.append('<p role="status">%s</p>' % esc('Course source search' if result['status'] == 'course_search' else result['status']))
    registry = journal.read_registry(base)
    options = []
    selected_source = (result or {}).get('source') or {
        key: (result or {}).get('citation', {}).get(key) for key in ('source_id', 'fingerprint')}
    for row in read['doc']['sources']:
        sid = row['source_object_id']
        record = registry.get(sid) or {}
        token = json.dumps({'source_id': sid, 'fingerprint': record.get('fingerprint')})
        options.append('<option value="%s"%s>%s</option>' % (esc(token),
            ' selected' if token == _one(retained or {}, 'source') or
            json.loads(token) == selected_source else '', esc(row.get('title') or sid)))
    source_field = '<label>Source <select name="source" required>%s</select></label>' % ''.join(options)
    out.append(form('choose_source', source_field, 'Choose source passages'))
    chosen = (result or {}).get('source') or (selected_source if selected_source.get('source_id') else None)
    if not chosen and options:
        try:
            chosen = json.loads(_one(retained or {}, 'source')) if _one(retained or {}, 'source') else {
                'source_id': read['doc']['sources'][0]['source_object_id'],
                'fingerprint': (registry.get(read['doc']['sources'][0]['source_object_id']) or {}).get('fingerprint')}
        except ValueError:
            chosen = None
    if chosen:
        try:
            choices = locator_choices(base, chosen)
            fields = hidden('source', json.dumps(chosen)) + '<label>Passage (Exact locator ID) <select name="locator" required>%s</select></label>' % ''.join(
                '<option value="%s"%s>%s</option>' % (esc(choice['ref']['locator_id']),
                ' selected' if choice['ref']['locator_id'] == (_one(retained or {}, 'locator') or
                (result or {}).get('citation', {}).get('locator_id')) else '', esc(choice['label']))
                for choice in choices)
            out.append(form('preview', fields, 'Preview exact passage'))
            if len(choices) == 256:
                out.append('<p>The picker shows the first 256 mapped occurrences in this source. Choose a smaller source for later ranges.</p>')
        except (ValueError, OSError, course.CourseError, journal.JournalError):
            out.append('<p role="status">This source needs revision, rights or assessment-route review. Choose another source.</p>')
    out.append('<p><a href="/course/%s/help">Ask about a selected source passage</a>. Review exact inclusion and the configured destination before sending.</p>' % esc(cid))
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
        out.append('<h3 id="research-exact-passage" tabindex="-1">Exact source preview</h3><pre class="research-source-preview">%s</pre>' % course_source_search.preview_text(result))
        out.append(course_source_search.return_control(url, result))
        out.append('<p>Source %s; accepted fingerprint %s; locator %s. Destination: this course\'s private _notes. A copied quote is a learner draft. Undo restores the previous note pair.</p>' % (
            esc(ref['source_id']), esc(ref['fingerprint']), esc(ref['locator_id'])))
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
    out.append(course_source_search.panel(base, result, retained,
        show_return=not bool(result and result.get('citation'))))
    query = (result or {}).get('query') or _one(retained or {}, 'query')
    match_case = (result or {}).get('match_case', _one(retained or {}, 'ignore_case') != 'yes')
    search_fields = ('<label>Query <input name="query" value="%s" maxlength="160" required></label>'
                     '<label><input type="checkbox" name="ignore_case" value="yes"%s> Ignore capitalization</label>') % (esc(query), '' if match_case else ' checked')
    out.append('''<style>
.context-search{min-width:0;overflow-wrap:anywhere;margin-block:24px}
.context-search label{display:block;margin-block:12px;line-height:1.5}
.context-search input:not([type]),.context-search input[type="text"]{display:block;box-sizing:border-box;width:100%;min-height:44px;font:inherit;padding:8px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--ink)}
.context-search input[type="checkbox"]{width:20px;height:20px;vertical-align:middle;margin-inline-end:8px}
.context-search button{min-height:44px;max-width:100%;font:inherit;white-space:normal;padding:10px 14px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--ink);margin-block:6px}
.context-search :focus-visible{outline:3px solid var(--accent);outline-offset:3px}
.context-search section{margin-block:20px}.context-search pre{white-space:pre-wrap;overflow-wrap:anywhere}
</style><section class="context-search" aria-labelledby="context-search-heading"><h3 id="context-search-heading">Search selected context</h3><p>Only saved passages and selected private notes are searched; no model or index is used. Matches retain exact original text locations.</p>''')
    out.append(form('search_context', search_fields, 'Search selected context'))
    if result and result['status'] in ('search', 'search_unavailable'):
        out.append('<p>Selected passages: %d. Selected notes: %d. Excluded sources: %d. Egress: none.</p>' % (
            result['selected_passages'], result['selected_notes'], result['excluded_sources']))
        if result['status'] == 'search_unavailable':
            out.append('<p role="alert">%s</p><ul>%s</ul>' % (esc(result['next_action']), ''.join(
                '<li>%s: %s</li>' % (esc(row.get('kind')), esc(row.get('state'))) for row in result['failures'])))
        else:
            out.append('<p role="status">%d hits on this page%s.</p>' % (len(result['hits']), '; more matches available' if result['truncated'] else ''))
            group = None
            for hit in result['hits']:
                label = ('Source %s, locator %s' % (hit['source_id'], hit['locator_id'])) if hit['kind'] == 'source' else 'Private learner note ' + hit['note_id']
                if label != group:
                    if group is not None:
                        out.append('</section>')
                    group = label
                    out.append('<section><h4>%s</h4>' % esc(label))
                out.append('<p>Code-point range %d:%d</p><pre>%s</pre>' % (hit['start'], hit['end'], esc(hit['excerpt'])))
                if hit['kind'] == 'source':
                    body = hidden('source', json.dumps({k: hit[k] for k in ('source_id', 'fingerprint')})) + hidden('locator', hit['locator_id'])
                    out.append(form('preview', body, 'Open exact source occurrence'))
            if group is not None:
                out.append('</section>')
            page_fields = hidden('query', query) + (hidden('ignore_case', 'yes') if not match_case else '')
            if result.get('offset'):
                out.append(form('search_context', page_fields + hidden('offset', max(0, result['offset'] - 32)), 'Previous matches'))
            if result.get('next_offset') is not None:
                out.append(form('search_context', page_fields + hidden('offset', result['next_offset']), 'Next matches'))
            elif result['truncated']:
                out.append('<p>Narrow the query to see matches beyond this bounded search.</p>')
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
