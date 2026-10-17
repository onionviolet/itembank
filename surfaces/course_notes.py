"""A disposable course view over the existing private note document."""
import hashlib
import urllib.parse

import course
import graph
import journal
import notes
import reading_desk
from surfaces import presentation
from surfaces import reading_desk as reader

PAGE_SIZE = 20
MAX_OFFSET = 100000


def _selection(fields):
    def one(key, default):
        values = fields.get(key, [default])
        if len(values) != 1:
            raise ValueError('Choose one note query and result page.')
        return values[0]
    query = one('notes_query', '')
    if len(query) > 160 or any(ord(char) < 32 or ord(char) == 127 for char in query):
        raise ValueError('Use up to 160 characters without control characters.')
    try:
        offset = int(one('notes_offset', '0'))
    except ValueError:
        raise ValueError('Choose a valid note result page.') from None
    if not 0 <= offset <= MAX_OFFSET:
        raise ValueError('Choose a valid note result page.')
    return query, offset


def anchor(note_id):
    return 'course-note-' + hashlib.sha256(note_id.encode()).hexdigest()[:24]


def _url(course_id, query='', offset=0):
    path = '/course/' + urllib.parse.quote(course_id, safe='') + '/learn'
    return path + '?' + urllib.parse.urlencode({'notes_query': query, 'notes_offset': offset}) + '#course-notes'


def reading_return(course_id, fields):
    """Construct a local return destination; never accept a caller's URL."""
    if fields.get('notes_return') != ['yes']:
        return None
    query, offset = _selection(fields)
    return {'href': _url(course_id, query, offset), 'label': 'Back to my course notes',
            'reading_query': '?' + urllib.parse.urlencode({
                'notes_return': 'yes', 'notes_query': query, 'notes_offset': offset})}


def collection(base, fields=None):
    """Read validated notes, retain broken anchors, and never read answer keys."""
    query, offset = _selection(fields or {})
    read = course.read_course(base)
    document = notes.read_note_document(reading_desk.note_root(base), read['object_id'])
    records = document['sidecar']['notes'] if document else []
    records = [note for note in records if note['status'] != 'deleted']
    objectives = {row['id']: row.get('statement') or row['id'] for row in read['doc']['objectives']}
    source_titles = {row['source_object_id']: row.get('title') or 'Source reference' for row in read['doc']['sources']}
    needle = query.strip().casefold()
    matched = [note for note in records if not needle or needle in '\n'.join([
        note['learner_wording'], *[objectives.get(oid, oid) for oid in note['objective_ids']]
    ]).casefold()]
    # Paginate before source admission. Only this page's linked readings need
    # validation; missing history cannot remove the learner's saved wording.
    try:
        accepted = course.accepted_reading_graph(base, read['fingerprint'])
        validated = graph.validate_reading_graph(accepted['doc'])
        parents = {row['supersedes_revision_id'] for row in validated['occurrences']}
        heads = [row for row in validated['occurrences'] if row['revision_id'] not in parents]
    except (course.CourseError, OSError, ValueError):
        heads = []
    rows = []
    link_cache = {}
    for note in matched[offset:offset + PAGE_SIZE]:
        links = []
        for target in note['targets']:
            if target['target_kind'] != 'source':
                continue
            key = (target['stable_id'], target['content_fingerprint'], target['locator'], target['quoted_context_hash'])
            if key not in link_cache:
                link_cache[key] = []
                for row in heads:
                    ref = row['source_ref']
                    if key[:3] != (ref['source_object_id'], ref['source_fingerprint'], ref['locator']):
                        continue
                    try:
                        passage = course.validate_reading_source(base, ref)['verbatim']
                        if notes.hash_quoted_context(passage) != target['quoted_context_hash']:
                            continue
                    except (course.CourseError, OSError, ValueError):
                        continue
                    title = validated['placements'].get(row['occurrence_id'], {}).get('title') or 'Source reading'
                    suffix = reading_return(read['object_id'], {
                        'notes_return': ['yes'], 'notes_query': [query], 'notes_offset': [str(offset)]})['reading_query']
                    link_cache[key].append({'title': title, 'href': reader.href(read['object_id'], row) + suffix})
            for link in link_cache[key]:
                if link not in links:
                    links.append(link)
        rows.append({'note': note, 'objectives': [objectives.get(oid, oid) for oid in note['objective_ids']],
                     'targets': [{'title': source_titles.get(target['stable_id'], 'Source reference')
                                  if target['target_kind'] == 'source' else target['target_kind'].replace('_', ' '),
                                  'locator': target['locator']} for target in note['targets']], 'links': links})
    return {'course_id': read['object_id'], 'query': query, 'offset': offset,
            'total': len(records), 'matched': len(matched), 'rows': rows}


def panel(base, fields=None):
    esc = presentation.esc
    out = ['<section class="course-notes" aria-labelledby="course-notes">'
           '<h3 id="course-notes" tabindex="-1">My course notes</h3>'
           '<p>Saved wording from your private course notebook. Search notes and their objectives.</p>']
    try:
        state = collection(base, fields)
    except ValueError as error:
        return ''.join(out) + '<p role="status">%s</p><p><a href="?notes_query=#course-notes">Show all my notes</a></p></section>' % esc(error)
    except (course.CourseError, journal.JournalError, OSError):
        return ''.join(out) + '<p role="status">Notes need recovery. Preserve the private note files and inspect their journal, then reload this course.</p></section>'
    out.append('<form method="get" action="%s#course-notes" role="search" aria-label="My course notes">'
               '<label>Search my notes <input name="notes_query" value="%s" maxlength="160"></label>'
               '<button type="submit">Search notes</button></form>' % (
                   '/course/' + urllib.parse.quote(state['course_id'], safe='') + '/learn', esc(state['query'])))
    if state['query']:
        out.append('<p><a href="%s">Show all my notes</a></p>' % esc(_url(state['course_id'])))
    if not state['total']:
        out.append('<p>No saved notes yet. Open a source reading and choose Write a note.</p>')
    elif not state['matched']:
        out.append('<p role="status">No notes match this query. Your %d saved notes are still here.</p>' % state['total'])
    else:
        out.append('<p role="status">Showing %d of %d matching notes (%d saved).</p>' % (
            len(state['rows']), state['matched'], state['total']))
        if not state['rows']:
            out.append('<p>This result page is empty. Return to the first page of this query.</p>'
                       '<a href="%s">First note results</a>' % esc(_url(state['course_id'], state['query'])))
    for row in state['rows']:
        note = row['note']
        out.append('<article id="%s" class="course-note"><p class="course-note-wording">%s</p>'
                   '<p class="reading-meta">%s · %s</p>' % (
                       anchor(note['note_id']), esc(note['learner_wording']),
                       esc('Learner wording' if note['authorship'] == 'learner' else 'Authored wording'), esc(note['status'].replace('_', ' '))))
        if row['objectives']:
            out.append('<p>Objectives: %s</p>' % esc('; '.join(row['objectives'])))
        for target in row['targets']:
            out.append('<p class="reading-meta">%s · %s</p>' % (
                esc(target['title']), esc(target['locator'])))
        for link in row['links']:
            out.append('<p><a href="%s">Open reading: %s</a></p>' % (esc(link['href']), esc(link['title'])))
        if note['targets'] and not row['links']:
            out.append('<p class="reading-meta">Reading link unavailable. Your wording and objective links are preserved.</p>')
        out.append('</article>')
    if state['offset']:
        out.append('<p><a href="%s">Previous notes</a></p>' % esc(_url(state['course_id'], state['query'], max(0, state['offset'] - PAGE_SIZE))))
    if state['offset'] + PAGE_SIZE < state['matched'] and state['offset'] + PAGE_SIZE <= MAX_OFFSET:
        out.append('<p><a href="%s">Next notes</a></p>' % esc(_url(state['course_id'], state['query'], state['offset'] + PAGE_SIZE)))
    return ''.join(out) + '</section>'


CSS = '''.course-notes{margin-block:32px;padding-block:24px;border-top:1px solid var(--line)}
.course-notes form{display:flex;flex-wrap:wrap;align-items:end;gap:12px}
.course-notes label{flex:1;min-width:0}.course-notes input{display:block;width:100%;box-sizing:border-box}
.course-notes input,.course-notes button,.course-notes a{min-height:44px}
.course-notes a{display:inline-flex;align-items:center;overflow-wrap:anywhere}
.course-note{border-top:1px solid var(--line);padding-block:20px;scroll-margin-block:96px}
.course-note-wording{white-space:pre-wrap;overflow-wrap:anywhere;max-width:var(--measure-prose)}'''
