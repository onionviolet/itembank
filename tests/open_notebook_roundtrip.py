"""The optional notebook companion stays local and never transfers course data."""

import io
import os
import sys
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from surfaces import open_notebook


class OpenNotebookCompanionTest(unittest.TestCase):
    def test_healthy_loopback_service_opens_in_separate_tab(self):
        with mock.patch.dict(os.environ, {
                "ITEMBANK_OPEN_NOTEBOOK_API_PORT": "5055",
                "ITEMBANK_OPEN_NOTEBOOK_UI_PORT": "8502"}), \
                mock.patch.object(open_notebook.urllib.request, "urlopen",
                                  return_value=io.BytesIO(b'{"status":"healthy"}')) as get:
            markup = open_notebook.panel()
        self.assertIn('href="http://127.0.0.1:8502/"', markup)
        self.assertIn('target="_blank"', markup)
        self.assertEqual(get.call_args.args[0].full_url,
                         "http://127.0.0.1:5055/health")

    def test_legacy_ok_health_response_remains_available(self):
        with mock.patch.object(open_notebook.urllib.request, "urlopen",
                               return_value=io.BytesIO(b'{"status":"ok"}')):
            markup = open_notebook.panel()
        self.assertIn('href="http://127.0.0.1:8502/"', markup)

    def test_unavailable_service_has_no_link(self):
        with mock.patch.object(open_notebook.urllib.request, "urlopen",
                               side_effect=OSError("offline")):
            markup = open_notebook.panel()
        self.assertIn("unavailable", markup)
        self.assertNotIn("href=", markup)

    def test_invalid_port_never_makes_request(self):
        with mock.patch.dict(os.environ, {
                "ITEMBANK_OPEN_NOTEBOOK_API_PORT": "https://example.com"}), \
                mock.patch.object(open_notebook.urllib.request, "urlopen") as get:
            markup = open_notebook.panel()
        self.assertIn("ports are invalid", markup)
        get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
