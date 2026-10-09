#!/usr/bin/env python3
"""Exercise browser selection without importing or requiring Playwright."""
import ast
import os
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'tools' / 'visual_qa.py'


class DriverError(Exception):
    """Stand in only for Playwright's typed launch error."""


def isolated_launcher():
    tree = ast.parse(SOURCE.read_text(encoding='utf-8'), filename=str(SOURCE))
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef)
                 and node.name == '_launch_browser']
    if len(functions) != 1:
        raise AssertionError('one isolated browser launcher is required')
    module = ast.Module(body=functions, type_ignores=[])
    namespace = {'os': os, 'PlaywrightError': DriverError}
    exec(compile(module, str(SOURCE), 'exec'), namespace)
    return namespace['_launch_browser']


class VisualLauncher(unittest.TestCase):
    def setUp(self):
        self.launch = isolated_launcher()
        self.chromium = mock.Mock()
        self.environment = mock.patch.dict(os.environ, {}, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def test_configured_channel_is_authoritative(self):
        os.environ['ITEMBANK_VISUAL_QA_CHANNEL'] = 'chrome-beta'
        browser, detail = self.launch(self.chromium)
        self.assertIs(browser, self.chromium.launch.return_value)
        self.chromium.launch.assert_called_once_with(channel='chrome-beta')
        self.assertEqual(detail, {'requested_channel': 'chrome-beta',
                                  'selected_channel': 'chrome-beta',
                                  'fallback_reason': None})

    def test_configured_missing_channel_does_not_fallback(self):
        os.environ['ITEMBANK_VISUAL_QA_CHANNEL'] = 'chrome-beta'
        error = DriverError("BrowserType.launch: Executable doesn't exist at "
                            '/synthetic/chrome-beta')
        self.chromium.launch.side_effect = error
        with self.assertRaises(DriverError) as raised:
            self.launch(self.chromium)
        self.assertIs(raised.exception, error)
        self.chromium.launch.assert_called_once_with(channel='chrome-beta')

    def test_default_prefers_bundled_chromium(self):
        browser, detail = self.launch(self.chromium)
        self.assertIs(browser, self.chromium.launch.return_value)
        self.chromium.launch.assert_called_once_with(channel=None)
        self.assertEqual(detail, {'requested_channel': None,
                                  'selected_channel': 'bundled-chromium',
                                  'fallback_reason': None})

    def test_empty_configured_channel_uses_bundled_default(self):
        os.environ['ITEMBANK_VISUAL_QA_CHANNEL'] = ''
        self.launch(self.chromium)
        self.chromium.launch.assert_called_once_with(channel=None)

    def test_missing_bundled_executable_tries_chrome_and_records_reason(self):
        reason = ("BrowserType.launch: Executable doesn't exist at "
                  '/synthetic/chromium_headless_shell/chrome-headless-shell')
        browser = object()
        self.chromium.launch.side_effect = [DriverError(reason + '\nInstall hint'),
                                            browser]
        actual, detail = self.launch(self.chromium)
        self.assertIs(actual, browser)
        self.assertEqual(self.chromium.launch.call_args_list,
                         [mock.call(channel=None), mock.call(channel='chrome')])
        self.assertEqual(detail, {'requested_channel': None,
                                  'selected_channel': 'chrome',
                                  'fallback_reason': reason})

    def test_missing_chrome_after_missing_bundle_is_a_genuine_failure(self):
        missing_bundle = DriverError(
            "BrowserType.launch: Executable doesn't exist at /synthetic/bundle")
        missing_chrome = DriverError(
            "BrowserType.launch: Chromium distribution 'chrome' is not found")
        self.chromium.launch.side_effect = [missing_bundle, missing_chrome]
        with self.assertRaises(DriverError) as raised:
            self.launch(self.chromium)
        self.assertIs(raised.exception, missing_chrome)
        self.assertEqual(self.chromium.launch.call_args_list,
                         [mock.call(channel=None), mock.call(channel='chrome')])

    def test_other_driver_errors_do_not_trigger_fallback(self):
        reasons = (
            '',
            'BrowserType.launch: Permission denied',
            'BrowserType.launch: Target page, context or browser has been closed',
            'BrowserType.launch: Running as root without --no-sandbox is not supported',
            "BrowserType.launch: security refusal\nCall log: Executable doesn't exist at /log",
        )
        for reason in reasons:
            with self.subTest(reason=reason):
                self.chromium.launch.reset_mock()
                error = DriverError(reason)
                self.chromium.launch.side_effect = error
                with self.assertRaises(DriverError) as raised:
                    self.launch(self.chromium)
                self.assertIs(raised.exception, error)
                self.chromium.launch.assert_called_once_with(channel=None)

    def test_non_driver_error_is_not_reclassified(self):
        error = RuntimeError("BrowserType.launch: Executable doesn't exist at /fake")
        self.chromium.launch.side_effect = error
        with self.assertRaises(RuntimeError) as raised:
            self.launch(self.chromium)
        self.assertIs(raised.exception, error)
        self.chromium.launch.assert_called_once_with(channel=None)


if __name__ == '__main__':
    unittest.main()
