"""HTTP boundary checks for the isolated synthetic-source prototype."""
import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from server import Handler, SOURCE, REVISION


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def post(self, body, origin=None):
        connection = HTTPConnection("127.0.0.1", self.server.server_port)
        headers = {"Content-Type": "application/json"}
        if origin:
            headers["Origin"] = origin
        connection.request("POST", "/api/ground", json.dumps(body), headers)
        response = connection.getresponse()
        result = response.status, json.loads(response.read())
        connection.close()
        return result

    def test_duplicate_requires_exact_occurrence(self):
        body = {"selection": "readings", "revision": REVISION}
        self.assertEqual(self.post(body)[0], 422)
        start = SOURCE.rindex("readings")
        body.update(selection_start=start, selection_end=start + len("readings"))
        status, result = self.post(body)
        self.assertEqual(status, 200)
        self.assertEqual(result["payload"]["selection_start"], start)

    def test_forged_source_and_rights_cannot_replace_server_source(self):
        status, result = self.post({"selection": "forged text", "revision": REVISION,
                                    "trusted_text": "forged text", "allow_read": True})
        self.assertEqual(status, 422)
        self.assertIsNone(result["payload"])

    def test_stale_revision(self):
        self.assertEqual(self.post({"selection": "rain gauge", "revision": "0" * 64})[0], 422)

    def test_cross_origin_denied(self):
        self.assertEqual(self.post({"selection": "rain gauge", "revision": REVISION},
                                   "https://example.org")[0], 403)


if __name__ == "__main__":
    unittest.main()
