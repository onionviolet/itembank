#!/usr/bin/env python3
"""Due practice is explicit, objective-scoped and recoverable on native routes."""
import json
import os
from pathlib import Path
import sys
import time
import unittest
import urllib.parse
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
import course
import evidence
import model
from surfaces import session
from a5_served_integration_roundtrip import request
import course_guidance_engine_roundtrip as guide_cases
from daemon_roundtrip import start_daemon


class DueJourney(unittest.TestCase):
    def test_due_preview_explicit_start_stale_refusal_and_restart(self):
        case = guide_cases.Guidance('test_due_practice_uses_existing_retention_and_current_binding')
        case.setUp()
        self.addCleanup(case.doCleanups)
        case.prepare()
        objective = model.load(str(case.bank))[0]['objective']
        os.utime(case.bank, (time.time() - 20 * 86400,) * 2)
        old = (datetime.now(timezone.utc) - timedelta(days=14)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        with patch.object(evidence, 'utc_now', return_value=old):
            for index in range(3):
                case.attempt = case.root / '_attempts' / ('session_old_%d.json' % index)
                case.start(count=1, objective=objective)
                session.do_submit(str(case.attempt), 'B', None)
        cid = course.read_course(str(case.base))['object_id']
        route = 'course/' + cid + '/practice'
        process, url, _ = start_daemon(str(case.root))
        try:
            before = guide_cases.snapshot(case.root)
            status, _, page = request(url + 'course/' + cid)
            self.assertEqual(status, 200)
            self.assertTrue('Start due practice' in page, page[page.find('id="course-guidance"'):page.find('id="course-guidance"') + 1800])
            self.assertIn('Choose another activity', page)
            self.assertEqual(guide_cases.snapshot(case.root), before, 'preview started a sitting')
            fields = {'action': 'start_due', 'bank': 'guidance_bank', 'objective': 'wrong-objective'}
            status, _, _ = request(url + route, fields)
            self.assertEqual(status, 400)
            self.assertEqual(guide_cases.snapshot(case.root), before, 'refused request mutated work')
            fields['objective'] = objective
            existing_ids = {json.loads(p.read_text())['session_id'] for p in (case.root / '_attempts').glob('*.json')}
            status, _, page = request(url + route, fields)
            self.assertEqual(status, 200)
            saved = next(json.loads(p.read_text()) for p in (case.root / '_attempts').glob('*.json')
                         if json.loads(p.read_text())['session_id'] not in existing_ids)
            sid = saved['session_id']
            self.assertIn(sid, page)
            target = '/quiz/guidance_bank?' + urllib.parse.urlencode({'mode': 'practice', 'session': sid, 'course': cid})
            self.assertEqual(saved['mode'], 'practice')
            self.assertTrue(all(model.load(str(case.bank))[i]['objective'] == objective for i in saved['items']))
            status, _, _ = request(url + route, fields)
            self.assertEqual(status, 400, 'an active selected sitting was replaced')
        finally:
            process.terminate()
            process.wait(timeout=8)
            if process.stdout:
                process.stdout.close()
        process, url, _ = start_daemon(str(case.root))
        try:
            status, _, page = request(urllib.parse.urljoin(url, target))
            self.assertEqual(status, 200)
            self.assertIn(sid, page)
        finally:
            process.terminate()
            process.wait(timeout=8)
            if process.stdout:
                process.stdout.close()


if __name__ == '__main__':
    unittest.main()
