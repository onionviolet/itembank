"""Supported reading and private source notes over the existing durable owners."""
import copy
import os

import course
import discovery
import evidence
import graph
import journal
import notes
import reading


def note_root(base):
    path = os.path.join(base, notes.NOTES_DIRNAME)
    if not discovery.inside_any_root(path, [base]):
        raise course.CourseError('notes.outside_root', 'Restore the private note root inside this course.')
    return path


def snapshot(base, body):
    with journal._journal_lock(base):
        acceptance_unknown = False
        try:
            read = course.accepted_reading_graph(base, body['expected_fingerprint'])
        except course.CourseError as error:
            if error.code != 'course.reading_acceptance_unknown':
                raise
            read = course.read_course(base)
            if read['state'] != 'clean' or read['fingerprint'] != body['expected_fingerprint']:
                raise
            # Historical evidence and private notes remain inspectable. This
            # fallback cannot read source content or authorize a new write.
            acceptance_unknown = True
        validated = graph.validate_reading_graph(read['doc'])
        rows = validated['occurrences']
        parents = {row['supersedes_revision_id'] for row in rows}
        heads = [row for row in rows if row['revision_id'] not in parents]
        selected = next((row for row in heads if row['occurrence_id'] == body['occurrence_id']
                         and row['revision_id'] == body['revision_id']), None)
        content = None
        available = {'state': 'occurrence-removed-or-revised'}
        if acceptance_unknown:
            available = {'state': 'course.reading_acceptance_unknown',
                         'message': 'Acceptance history is missing. Restore it before adding reading declarations or notes.'}
        elif selected:
            available = reading.availability(base, selected['source_ref'])
            try:
                content = course.validate_reading_source(base, selected['source_ref'])['verbatim']
                available = {'state': 'available'}
            except (course.CourseError, OSError, ValueError) as error:
                available = {'state': getattr(error, 'code', 'source-unavailable')}
        state = evidence.reading_state(reading._log(base), read['object_id'], body['occurrence_id'], body['revision_id'])
        document = None
        note_error = None
        try:
            document = notes.read_note_document(note_root(base), read['object_id'])
        except (journal.JournalError, OSError):
            note_error = 'Notes need recovery. Preserve your draft and inspect the private note journal.'
        records = copy.deepcopy(document['sidecar']['notes']) if document else []
        for note in records:
            source_targets = [target for target in note['targets'] if target['target_kind'] == 'source']
            note['anchor_state'] = 'Anchor unavailable. Wording and objectives retained.'
            for target in source_targets:
                matches = [row for row in heads if row['source_ref']['source_object_id'] == target['stable_id']
                           and row['source_ref']['source_fingerprint'] == target['content_fingerprint']
                           and row['source_ref']['locator'] == target['locator']]
                for row in ([] if acceptance_unknown else matches):
                    try:
                        course.validate_reading_source(base, row['source_ref'])
                        note['anchor_state'] = 'Anchored to shared source'
                        break
                    except (course.CourseError, OSError, ValueError):
                        pass
        return {'occurrence': selected, 'occurrences': heads, 'content': content,
                'placements': validated['placements'], 'availability': available, 'reading_state': state, 'notes': records,
                'notes_fingerprint': document['fingerprint'] if document else None,
                'note_error': note_error, 'expected_fingerprint': read['fingerprint']}


def save_note(base, body, actor_kind='human'):
    if len(body['wording']) > 20000:
        raise course.CourseError('notes.too_long', 'Keep this note below 20000 characters.')
    if actor_kind != 'human':
        raise course.CourseError('notes.learner_required', 'Only the learner saves personal wording here.')
    with journal._journal_lock(base):
        read, occurrence = reading._current(base, body)
        root = note_root(base)
        document = notes.read_note_document(root, read['object_id'])
        existing = next((n for n in document['sidecar']['notes'] if n['note_id'] == body['note_id']), None) if document else None
        target = notes.target_record('source', occurrence['source_ref']['source_object_id'],
                                     occurrence['source_ref']['source_fingerprint'],
                                     occurrence['source_ref']['locator'], notes.hash_quoted_context(
                                         course.validate_reading_source(base, occurrence['source_ref'])['verbatim']))
        if existing:
            if existing['learner_wording'] != body['wording'] or existing['targets'] != [target]:
                raise course.CourseError('notes.retry_conflict', 'This note identity already contains different wording. Keep your draft.')
            return {'status': 'saved', 'note_id': existing['note_id'], 'fingerprint': document['fingerprint']}
        note = notes.note_record(read['object_id'], occurrence['objective_ids'], 'learner_claim',
                                 body['wording'], [target], status='learner_accepted')
        note['note_id'] = body['note_id']
        sidecar = copy.deepcopy(document['sidecar']) if document else {
            'schema_version': notes.NOTE_SCHEMA_VERSION, 'note_document_id': note['note_document_id'],
            'course_id': read['object_id'], 'notes': []}
        note['note_document_id'] = sidecar['note_document_id']
        sidecar['notes'].append(note)
        markdown = (document['markdown'] if document else '# My notes\n') + '\n\n' + body['wording'] + '\n'
        result = notes.write_note_document(root, read['object_id'], markdown, sidecar,
                                           expected_fingerprint=body['notes_fingerprint'])
        return {'status': 'saved', 'note_id': note['note_id'], 'fingerprint': result['fingerprint']}


def operation(base, operation, body, actor_kind, actor_name):
    try:
        return snapshot(base, body) if operation == 'reading_view' else save_note(base, body, actor_kind)
    except (journal.JournalError, OSError, ValueError) as error:
        raise course.CourseError(getattr(error, 'code', 'notes.save_failed'),
                                'The operation was not accepted. Keep your note draft. Reload or recover the private note journal.') from None
