"""Read-only literal retrieval over admitted course sources, with exact locators."""
import hashlib
import json
import os
import re
import urllib.parse

import course
import discovery
import identity
import journal
import source_adapters
from surfaces import presentation

MAX_SOURCES = 64
MAX_PASSAGES = 128
MAX_HITS = 32
MAX_OFFSET = 4096
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_CORPUS_BYTES = 8 * 1024 * 1024


def validate_query(query):
    if (not isinstance(query, str) or not query.strip() or len(query) > 160 or
            any(ord(char) < 32 or ord(char) == 127 for char in query)):
        raise ValueError('Enter one literal query of 1 to 160 characters without control characters.')
    return query


def _locators(base, record):
    relative = record.get('path')
    if not isinstance(relative, str) or os.path.isabs(relative):
        raise ValueError('The registered source path is unavailable.')
    path = os.path.join(base, relative)
    sidecar = source_adapters.sidecar_path_for(path)
    if not all(discovery.inside_any_root(item, [base]) for item in (path, sidecar)):
        raise ValueError('The source or its locator leaves the approved course root.')
    size = os.path.getsize(path)
    if size > MAX_FILE_BYTES:
        raise ValueError('Choose a source smaller than 2 MiB for this search.')
    with open(sidecar, 'rb') as stream:
        raw = stream.read(MAX_FILE_BYTES + 1)
    if len(raw) > MAX_FILE_BYTES:
        raise ValueError('The source locator sidecar exceeds this search limit.')
    document = json.loads(raw)
    if not isinstance(document, dict):
        raise ValueError('Repair the source locator sidecar.')
    locators = document.get('locators')
    if not isinstance(locators, list) or not all(isinstance(item, dict) for item in locators):
        raise ValueError('Repair the source locator sidecar.')
    return size, [item['id'] for item in locators if item.get('span_id') is not None]


def _failure(exc):
    if isinstance(exc, ValueError) and str(exc).startswith('Assessment sources'):
        return 'assessment', 'Use the runtime practice or test route for this source.'
    if isinstance(exc, OSError):
        return 'unavailable', 'Restore access to the source and its locator sidecar.'
    if isinstance(exc, course.CourseError) or 'changed' in str(exc):
        return 'stale', 'Review the source and accepted locator revision.'
    return 'unsupported', 'Review source access, bounds and locator provenance.'


def search(base, query, *, match_case=True, offset=0):
    """Never discover files, include private notes, mutate scope or invoke a model."""
    from surfaces import research_context

    validate_query(query)
    if type(match_case) is not bool or type(offset) is not int or not 0 <= offset <= MAX_OFFSET:
        raise ValueError('Choose a valid search mode and a result offset from 0 to 4096.')
    capture_limit = offset + MAX_HITS + 1
    read, _admitted = research_context._info(base)
    registry = journal.read_registry(base)
    rows = read['doc']['sources']
    result = {'status': 'course_search', 'query': query, 'match_case': match_case,
              'offset': offset, 'next_offset': None, 'egress': 'none',
              'sources_total': len(rows), 'sources_searched': 0, 'passages_searched': 0,
              'hits': [], 'omitted_sources': [], 'limited': len(rows) > MAX_SOURCES}
    corpus_bytes = 0
    for source_index, source in enumerate(rows[:MAX_SOURCES]):
        sid = source['source_object_id']
        title = source.get('title') or sid
        record = registry.get(sid) or {}
        reason = None
        state = 'unavailable'
        source_hits = []
        if record.get('kind') != 'source':
            reason = 'The source is not currently registered.'
        elif not all(identity.rights_granted(record.get('rights'), right) for right in ('read', 'quote')):
            state, reason = 'rights_unavailable', 'Review the source read and quote rights.'
        else:
            try:
                size, locators = _locators(base, record)
                if corpus_bytes + size > MAX_CORPUS_BYTES:
                    result['limited'] = True
                    break
                corpus_bytes += size
                current_state = journal.object_state(base, sid)
                if current_state != 'clean':
                    state = 'unavailable' if current_state in ('missing', 'unavailable') else 'stale'
                    reason = 'Review source access and its accepted revision before searching.'
                    locators = []
                if not locators and not reason:
                    state, reason = 'empty', 'This source has no mapped passages.'
                last_ref = None
                visited = 0
                for locator_index, locator_id in enumerate(locators):
                    if result['passages_searched'] >= MAX_PASSAGES:
                        result['limited'] = True
                        break
                    ref = {'source_id': sid, 'fingerprint': record['fingerprint'],
                           'locator_id': locator_id}
                    passage = research_context._safe_source(base, ref)
                    last_ref = ref
                    visited = locator_index + 1
                    result['passages_searched'] += 1
                    text = passage['text']
                    for start, end in research_context._literal_ranges(text, query, match_case):
                        if len(result['hits']) + len(source_hits) == capture_limit:
                            result['limited'] = True
                            break
                        source_hits.append(dict(ref, title=title, start=start, end=end,
                            origin=passage['origin'],
                            excerpt=text[max(0, start - 80):min(len(text), end + 80)]))
                    if len(result['hits']) + len(source_hits) == capture_limit:
                        result['limited'] = True
                        break
                if result['passages_searched'] >= MAX_PASSAGES and (
                        visited < len(locators) or source_index + 1 < len(rows)):
                    result['limited'] = True
                # Re-admit the source/sidecar after scanning. A refused source
                # contributes no snippets, including hits collected earlier.
                if last_ref:
                    research_context._safe_source(base, last_ref)
                    current = journal.read_registry(base).get(sid) or {}
                    if not identity.rights_granted(current.get('rights'), 'quote'):
                        state, reason = 'rights_unavailable', 'Source quote rights changed during search.'
                    else:
                        result['sources_searched'] += 1
            except (ValueError, OSError, KeyError, TypeError, course.CourseError, journal.JournalError) as exc:
                state, reason = _failure(exc)
        if reason:
            result['omitted_sources'].append({'source_id': sid, 'title': title,
                                             'state': state, 'reason': reason})
        else:
            result['hits'].extend(source_hits)
        if result['passages_searched'] >= MAX_PASSAGES or len(result['hits']) == capture_limit:
            break
    # A source scanned early may change while a later source is being searched.
    # Recheck every source contributing hits before returning those snippets.
    stopped_at_hit_limit = len(result['hits']) == capture_limit
    matched = {hit['source_id']: hit for hit in result['hits']}
    for sid, hit in matched.items():
        try:
            current = journal.read_registry(base).get(sid) or {}
            if not all(identity.rights_granted(current.get('rights'), right) for right in ('read', 'quote')):
                state, reason = 'rights_unavailable', 'Review source read and quote rights.'
            else:
                research_context._safe_source(base, {key: hit[key] for key in ('source_id', 'fingerprint', 'locator_id')})
                continue
        except (ValueError, OSError, course.CourseError, journal.JournalError) as exc:
            state, reason = _failure(exc)
        if reason:
            result['hits'] = [item for item in result['hits'] if item['source_id'] != sid]
            result['sources_searched'] -= 1
            result['omitted_sources'].append({'source_id': sid, 'title': hit['title'],
                'state': state, 'reason': reason})
            if stopped_at_hit_limit:
                result['retry_required'] = True
    if course.read_course(base)['fingerprint'] != read['fingerprint']:
        raise ValueError('The course source list changed. Keep the query and search its current revision again.')
    if result.get('retry_required'):
        # Removed early hits consumed the bounded scan. A sparse page cannot
        # truthfully represent the end of the still-current later matches.
        result['hits'] = []
    result['more_matches'] = len(result['hits']) > offset + MAX_HITS
    if result['more_matches'] and offset + MAX_HITS <= MAX_OFFSET:
        result['next_offset'] = offset + MAX_HITS
    result['hits'] = result['hits'][offset:offset + MAX_HITS]
    return result


def admit_match(base, result, fields):
    """Validate a presentation-only match against the newly admitted passage."""
    from surfaces import research_context

    if not any(key in fields for key in ('return_query', 'match_start', 'match_end',
                                        'return_ignore_case', 'return_offset')):
        return result
    query = validate_query(research_context._one(fields, 'return_query'))
    ignore_case = research_context._one(fields, 'return_ignore_case')
    if ignore_case not in ('', 'yes'):
        raise ValueError('Choose whether to ignore capitalization.')
    record = journal.read_registry(base).get(result['citation']['source_id']) or {}
    if not identity.rights_granted(record.get('rights'), 'quote'):
        raise ValueError('Review source quote rights before opening a search match.')
    try:
        start = int(research_context._one(fields, 'match_start'))
        end = int(research_context._one(fields, 'match_end'))
        offset = int(research_context._one(fields, 'return_offset', '0'))
    except ValueError:
        raise ValueError('Retain the original search match range.') from None
    text = result['passage']['text']
    if not 0 <= offset <= MAX_OFFSET:
        raise ValueError('Choose a valid result page.')
    matches = (text[start:end] == query if not ignore_case else
               text[start:end].casefold() == query.casefold())
    if not 0 <= start < end <= len(text) or not matches:
        raise ValueError('This match changed. Return to the query and search again.')
    return dict(result, return_query=query, match_start=start, match_end=end,
                match_case=not ignore_case, offset=offset)


def match_anchor(hit):
    """Anchor the occurrence and accepted revision, independently of row order."""
    identity = [hit[key] for key in ('source_id', 'fingerprint', 'locator_id', 'start', 'end')]
    raw = json.dumps(identity, separators=(',', ':')).encode('utf-8')
    return 'course-search-occurrence-' + hashlib.sha256(raw).hexdigest()[:32]


def validate_return_match(value):
    if not isinstance(value, str) or not re.fullmatch(r'course-search-occurrence-[0-9a-f]{32}', value):
        raise ValueError('Return to a match from the current course source search.')
    return value


def return_control(url, result=None, retained=None):
    """A navigation hint never admits a source or changes research inclusion."""
    from surfaces import research_context

    result, retained = result or {}, retained or {}
    query = result.get('return_query') or research_context._one(retained, 'return_query')
    if not query:
        return ''
    esc = presentation.esc
    offset = result.get('offset', research_context._one(retained, 'return_offset', '0'))
    ignore_case = (not result['match_case'] if 'match_case' in result else
                   research_context._one(retained, 'return_ignore_case') == 'yes')
    target = 'course-source-search'
    fields = [('operation', 'search_course_sources'), ('query', query), ('offset', offset)]
    if result.get('citation') and 'match_start' in result:
        target = match_anchor(dict(result['citation'], start=result['match_start'], end=result['match_end']))
        fields.append(('return_match', target))
    if ignore_case:
        fields.append(('ignore_case', 'yes'))
    hidden = ''.join('<input type="hidden" name="%s" value="%s">' % (name, esc(value))
                     for name, value in fields)
    return ('<form class="context-search course-search-return" method="post" action="%s#%s">%s'
            '<button>Return to this course source search</button></form>') % (url, target, hidden)


def preview_text(result):
    """Keep exact Unicode offsets in the static, escaped source preview."""
    text = result['passage']['text']
    if not result.get('return_query'):
        return presentation.esc(text)
    start, end = result['match_start'], result['match_end']
    return (presentation.esc(text[:start]) + '<span id="course-source-match" tabindex="-1"><mark>' +
            presentation.esc(text[start:end]) + '</mark></span>' + presentation.esc(text[end:]))


def excerpt_text(hit, query):
    """Mark this exact occurrence, even when its context repeats the query."""
    text = hit['excerpt']
    start = min(hit['start'], 80)
    end = start + hit['end'] - hit['start']
    if text[start:end].casefold() != query.casefold():
        return presentation.esc(text)
    return (presentation.esc(text[:start]) + '<mark>' + presentation.esc(text[start:end]) +
            '</mark>' + presentation.esc(text[end:]))


def panel(base, result=None, retained=None, *, show_return=True):
    """Native script-free search, source-match preview and exact-query return."""
    from surfaces import research_context

    esc = presentation.esc
    read, _admitted = research_context._info(base)
    url = '/course/%s/research' % urllib.parse.quote(read['object_id'], safe='')
    result, retained = result or {}, retained or {}
    query = result.get('query') or result.get('return_query') or research_context._one(retained, 'query') or research_context._one(retained, 'return_query')
    ignore_case = (not result['match_case'] if 'match_case' in result else
                   research_context._one(retained, 'ignore_case') == 'yes' or
                   research_context._one(retained, 'return_ignore_case') == 'yes')
    try:
        offset = int(result.get('offset', research_context._one(retained, 'return_offset') or
                                research_context._one(retained, 'offset', '0')))
        if not 0 <= offset <= MAX_OFFSET:
            offset = 0
    except (TypeError, ValueError):
        offset = 0
    def hidden(name, value):
        return '<input type="hidden" name="%s" value="%s">' % (name, esc(value))
    def form(operation, body, label, fragment='course-source-search', describedby=''):
        description = ' aria-describedby="%s"' % esc(describedby) if describedby else ''
        return '<form method="post" action="%s#%s">%s%s<button%s>%s</button></form>' % (
            url, fragment, hidden('operation', operation), body, description, esc(label))
    out = ['<style>.course-search-match{padding-block:20px;border-top:1px solid var(--line);scroll-margin-block:96px}'
        '.course-search-match:target{border-inline-start:3px solid var(--accent);padding-inline-start:16px;outline:2px solid var(--accent);outline-offset:4px}'
        '.course-search-position{font-size:var(--text-xs);color:var(--mut)}'
        '.course-search-recovery a{display:inline-flex;align-items:center;min-height:44px}'
        '.course-search-match h4{margin:0}.course-search-match .course-search-location{'
        'font-size:var(--text-xs);color:var(--mut);margin-block:6px 12px}'
        '.course-search-match pre{font:inherit;line-height:1.6;margin-block:12px;max-width:var(--measure-prose);'
        'white-space:pre-wrap;overflow-wrap:anywhere}.course-search-match mark{'
        'background:var(--accent-soft);color:var(--ink);font-weight:600;text-decoration:underline;'
        'text-underline-offset:3px}</style>',
        '<section class="context-search" aria-labelledby="course-source-search"><h3 id="course-source-search" tabindex="-1">Search course sources</h3>',
        '<p>Search registered source passages locally, without selecting them for a model. Literal search excludes private notes, assessments and unregistered files. Read and quote rights are required.</p>',
        form('search_course_sources', '<label>Course source query <input name="query" value="%s" maxlength="160" required></label>' % esc(query) +
             '<label><input type="checkbox" name="ignore_case" value="yes"%s> Ignore capitalization</label>' % (' checked' if ignore_case else ''), 'Search course sources')]
    def page_fields(page):
        return hidden('query', query) + hidden('offset', page) + (hidden('ignore_case', 'yes') if ignore_case else '')
    if show_return:
        out.append(return_control(url, result, retained))
    if result.get('status') != 'course_search':
        return ''.join(out) + '</section>'
    out.append('<p role="status">%d hits. Searched %d of %d registered sources and %d passages. Egress: none.</p>' % (
        len(result['hits']), result['sources_searched'], result['sources_total'], result['passages_searched']))
    if result.get('retry_required'):
        out.append('<p role="status">A source changed during this bounded search. No matches are released from this page. Retry the same query and page against current source revisions.</p>')
        out.append(form('search_course_sources', page_fields(offset), 'Retry current course search page'))
    if result['limited']:
        out.append('<p role="status">Search coverage is bounded to 64 sources, 128 passages and 8 MiB, with 32 hits per page. More content or matches may remain.</p>')
    if offset:
        out.append('<p>Result offset: %d. This page rechecks current source revisions and rights.</p>' % offset)
        out.append(form('search_course_sources', page_fields(max(0, offset - MAX_HITS)), 'Previous course search results'))
    if result.get('next_offset') is not None:
        out.append(form('search_course_sources', page_fields(result['next_offset']), 'Next course search results'))
    elif result.get('more_matches'):
        out.append('<p role="status">The result offset limit was reached. Use a more specific query to find later matches.</p>')
    returned = result.get('return_match')
    anchors = {match_anchor(hit) for hit in result['hits']}
    if returned and returned not in anchors:
        out.append('<p id="%s" tabindex="-1" role="status">That occurrence is no longer in these results. The query and page are preserved. Review the source notices below or search again.</p>' % esc(returned))
        out.append(form('search_course_sources', page_fields(offset) + hidden('return_match', returned),
                        'Retry this course source search', returned))
        out.append('<p class="course-search-recovery"><a href="#course-source-search">Edit course source query</a></p>')
    for omitted in result['omitted_sources']:
        out.append('<p>%s: %s. %s</p>' % (esc(omitted['title']), esc(omitted['state'].replace('_', ' ')), esc(omitted['reason'])))
    for index, hit in enumerate(result['hits']):
        origin = ', '.join('%s %s' % (key.replace('_', ' '), value) for key, value in hit['origin'].items()
                           if isinstance(value, (str, int)) and key != 'kind')
        title_id, location_id = 'course-search-hit-%d' % index, 'course-search-location-%d' % index
        anchor = match_anchor(hit)
        position_id = 'course-search-position-%d' % index
        position = 'Match %d%s' % (offset + index + 1, ', returned occurrence' if returned == anchor else '')
        out.append('<section id="%s" class="course-search-match" tabindex="-1" aria-labelledby="%s" aria-describedby="%s"><p id="%s" class="course-search-position">%s</p><h4 id="%s">%s</h4>'
            '<p id="%s" class="course-search-location">%s</p><pre>%s</pre>'
            '<details><summary>Exact location</summary><p>Locator %s, character range %d:%d.</p></details>' % (
                anchor, title_id, position_id, position_id, esc(position), title_id, esc(hit['title']), location_id, esc(origin or hit['locator_id']),
                excerpt_text(hit, query), esc(hit['locator_id']), hit['start'], hit['end']))
        body = hidden('source', json.dumps({key: hit[key] for key in ('source_id', 'fingerprint')})) + hidden('locator', hit['locator_id'])
        body += hidden('return_query', query) + hidden('match_start', hit['start']) + hidden('match_end', hit['end'])
        body += hidden('return_offset', offset) + (hidden('return_ignore_case', 'yes') if ignore_case else '')
        out.append(form('preview', body, 'Open exact course search match', 'course-source-match',
                        position_id + ' ' + title_id + ' ' + location_id) + '</section>')
    return ''.join(out) + '</section>'
