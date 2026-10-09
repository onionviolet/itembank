#!/usr/bin/env python3
"""Keep failed script diagnostics and deferred delivery counts observable."""
import contextlib
import io
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import preflight


class DiagnosticSummary(unittest.TestCase):
    def run_scripts(self, source_only):
        apps = sorted(preflight.APP_BUILD_TESTS)
        names = apps + ['daemon_roundtrip.py', 'model_phase_roundtrip.py',
                        'z_after_lan_roundtrip.py']
        invoked = []

        def run(command):
            name = Path(command[-1]).name
            invoked.append(name)
            if name in ('daemon_roundtrip.py', 'model_phase_roundtrip.py'):
                return 1, 'earlier passing case\n' * 30 + name + ': timed out\n'
            return 0, 'passed\n'

        output = io.StringIO()
        with mock.patch.object(preflight.os, 'listdir', return_value=names), \
                mock.patch.object(preflight, 'run', side_effect=run), \
                contextlib.redirect_stdout(output):
            ok, message = preflight.gate_tests(source_only=source_only)
        return ok, message, invoked, apps

    def test_source_only_failure_preserves_counts_tracebacks_and_later_scripts(self):
        ok, message, invoked, apps = self.run_scripts(True)
        self.assertFalse(ok)
        self.assertIn('6 discovered, 3 executed, 1 passed, 2 failed, 3 deferred', message)
        self.assertIn('daemon_roundtrip.py: timed out', message)
        self.assertIn('model_phase_roundtrip.py: timed out', message)
        self.assertEqual(invoked, ['daemon_roundtrip.py', 'model_phase_roundtrip.py',
                                   'z_after_lan_roundtrip.py'])
        for name in apps:
            self.assertIn(name, message)
        self.assertEqual(message.count('earlier passing case'), 60)

    def test_default_failure_runs_delivery_scripts_and_does_not_defer_lan(self):
        ok, message, invoked, apps = self.run_scripts(False)
        self.assertFalse(ok)
        self.assertIn('6 discovered, 6 executed, 4 passed, 2 failed, 0 deferred', message)
        self.assertEqual(set(invoked), set(apps) | {'daemon_roundtrip.py',
                         'model_phase_roundtrip.py', 'z_after_lan_roundtrip.py'})
        self.assertNotIn('App-build checks deferred:', message)

    def test_success_reports_the_same_denominators(self):
        output = io.StringIO()
        with mock.patch.object(preflight.os, 'listdir', return_value=['pass.py']), \
                mock.patch.object(preflight, 'run', return_value=(0, 'ok')), \
                contextlib.redirect_stdout(output):
            ok, message = preflight.gate_tests(source_only=True)
        self.assertTrue(ok)
        self.assertIn('1 discovered, 1 executed, 1 passed, 0 failed, 0 deferred', message)


if __name__ == '__main__':
    unittest.main()
