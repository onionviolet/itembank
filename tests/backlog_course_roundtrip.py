#!/usr/bin/env python3
"""Prerequisite context, bounded source discovery and revision impact."""
import json
import html
import re
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import course
import evidence
import graph
import journal
from surfaces import course_workbench as cw, session
from course_guidance_journey_roundtrip import fixture, snapshot, served, get


def relation(base, source):
    read = course.read_course(base)
    doc = read['doc']
    graph.add_objective(doc, 'Transfer the fictional rule', objective_id='synthetic:transfer')
    graph.add_edge(doc, source, 'prerequisite-of', 'synthetic:transfer', authority='authored',
                   rationale='Use the fictional rule before combining boundaries.', confidence='high')
    course.write_course(base, doc, read['fingerprint'], 'human', 'test')
    return course.read_course(base)['doc']


class BacklogCourse(unittest.TestCase):
    def test_exact_prerequisites_empty_pending_withheld_retracted_and_read_only(self):
        with fixture() as (root, base, banks, info):
            doc = relation(base, info['objective'])
            before = snapshot(root)
            initial = cw.prerequisite_context(root, base, doc, banks)
            row = initial['objectives']['synthetic:transfer'][0]
            self.assertIn('No attributable', row['evidence'])
            self.assertEqual(row['authority'], 'authored')
            self.assertEqual(row['confidence'], 'high')
            self.assertEqual(snapshot(root), before)
            out = root / '_attempts' / 'session_pending.json'
            start = session.do_start(str(base / 'pending.md'), {'count': 1, 'seed': 0},
                                     'practice', str(out), False)
            session.do_submit(str(out), 'PRIVATE SYNTHETIC EXPLANATION', None)
            before = snapshot(root)
            current = cw.prerequisite_context(root, base, doc, banks)
            self.assertIn('1 pending review', current['objectives']['synthetic:transfer'][0]['evidence'])
            self.assertNotIn('PRIVATE', json.dumps(current))
            self.assertEqual(snapshot(root), before)
            exam = root / '_attempts' / 'session_exam.json'
            session.do_start(str(base / 'symbols.md'), {'count': 2, 'seed': 0}, 'exam', str(exam), False)
            session.do_submit(str(exam), 'A', None)
            current = cw.prerequisite_context(root, base, doc, banks)
            self.assertIn('1 with feedback withheld', current['objectives']['synthetic:transfer'][0]['evidence'])
            events = list(evidence.live_events(evidence.log_path(base)))
            pending = next(e for e in events if e.get('event_type') == 'response'
                           and e.get('session_id') == start['session_id'])
            evidence.append_event(evidence.log_path(base), evidence.retraction_event(pending['event_id'], 'Synthetic withdrawal'))
            current = cw.prerequisite_context(root, base, doc, banks)
            self.assertIn('0 pending review', current['objectives']['synthetic:transfer'][0]['evidence'])
            with patch.object(cw, 'review_history', return_value={'state': 'error', 'rows': []}):
                current = cw.prerequisite_context(root, base, doc, banks)
            self.assertIn('unavailable or incomplete', current['objectives']['synthetic:transfer'][0]['evidence'])
            # Similar titles do not transfer evidence to a new objective ID.
            doc['edges'][0]['source'] = 'new:identity'
            doc['objectives'].append(dict(doc['objectives'][0], id='new:identity'))
            current = cw.prerequisite_context(root, base, doc, banks)
            self.assertIn('No attributable', current['objectives']['synthetic:transfer'][0]['evidence'])

    def test_unknown_relation_missing_endpoint_and_cycle_stay_visible(self):
        with fixture() as (root, base, banks, info):
            doc = relation(base, info['objective'])
            doc['edges'][0]['edge_type'] = 'invented-relation'
            self.assertEqual(cw.prerequisite_context(root, base, doc, banks)['objectives'], {})
            doc['edges'][0]['edge_type'] = 'prerequisite-of'
            doc['edges'][0]['source'] = 'missing'
            self.assertTrue(cw.prerequisite_context(root, base, doc, banks)['failures'])
            doc['edges'][0]['source'] = info['objective']
            graph.add_edge(doc, 'synthetic:transfer', 'prerequisite-of', info['objective'])
            self.assertTrue(any('cycle' in x for x in cw.prerequisite_context(root, base, doc, banks)['failures']))

    def test_inventory_bounds_exclusions_identity_and_source_impact(self):
        with fixture() as (root, base, banks, info):
            doc = relation(base, info['objective'])
            hidden = base / '_notes'
            hidden.mkdir(exist_ok=True)
            (hidden / 'private.txt').write_text('PRIVATE NOTE')
            (base / 'large.bin').write_bytes(b'x' * (2 * 1024 * 1024 + 1))
            (base / 'outside.txt').symlink_to(root.parent)
            before = snapshot(root)
            inventory = cw.source_inventory(base, doc)
            self.assertEqual(snapshot(root), before)
            self.assertFalse(any('_notes' in r['path'] for r in inventory['rows']))
            self.assertTrue(any(r['kind'] == 'registered source' and r['href'] for r in inventory['rows']))
            self.assertTrue(any(r['path'] == 'large.bin' and r['state'] == 'unavailable' for r in inventory['rows']))
            source = journal.read_registry(base)[info['source_id']]
            path = base / source['path']
            path.write_text('CHANGED SOURCE TEXT MUST NOT BE DISCLOSED', encoding='utf-8')
            before = snapshot(root)
            impact = cw.source_impact(base, doc, info['source_id'])
            self.assertNotEqual(impact['accepted'], impact['current'])
            self.assertIn(info['objective'], impact['objectives'])
            self.assertEqual(snapshot(root), before)
            with served(root) as url:
                markup = get(url, '/course/synthetic/sources?source=0&inventory=1')
                self.assertIn('Source revision needs review', markup)
                self.assertIn('Affected objectives', markup)
                self.assertNotIn('CHANGED SOURCE TEXT MUST NOT BE DISCLOSED', markup)

    def test_native_map_source_and_return_do_not_append_evidence(self):
        with fixture() as (root, base, banks, info):
            relation(base, info['objective'])
            before = snapshot(root)
            with served(root) as url:
                markup = get(url, '/course/synthetic/map')
                self.assertIn('Builds on', markup)
                self.assertIn('Use the fictional rule before combining boundaries.', markup)
                links = re.findall(r'href="([^"<>]*/map(?:\?[^"<>]*)?#objective-\d+)"', markup)
                self.assertTrue(links, 'No prerequisite map link was rendered')
                self.assertIn('Use the fictional rule', get(url, html.unescape(links[-1])))
                self.assertNotIn('CORRECT:', markup)
                self.assertIn('Source text', get(url, '/course/synthetic/sources?source=0'))
                self.assertIn('Builds on', get(url, '/course/synthetic/map#objective-1'))
            self.assertEqual(snapshot(root), before)


if __name__ == '__main__':
    unittest.main()
