import unittest
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import (
    HTTPStatus,
    CaseInsensitiveDict,
    SimplePBKDF2,
    CSVExporter,
    ExpandedMimeDatabase,
    TrieRouter,
    Request,
    Response
)

class TestHTTPServerComponents(unittest.TestCase):
    def test_case_insensitive_dict(self):
        d = CaseInsensitiveDict()
        d["Content-Type"] = "text/html"
        self.assertEqual(d["content-type"], "text/html")
        self.assertEqual(d["Content-Type"], "text/html")
        self.assertTrue("CONTENT-TYPE" in d)
        self.assertEqual(d.get("Accept-Encoding", "gzip"), "gzip")

    def test_pbkdf2_hashing(self):
        pwd = "secure_student_password_2026"
        hashed = SimplePBKDF2.hash_password(pwd)
        self.assertTrue(SimplePBKDF2.verify_password(pwd, hashed))
        self.assertFalse(SimplePBKDF2.verify_password("wrong_password", hashed))

    def test_csv_exporter(self):
        feedbacks = [
            {"teacher_id": 1, "rating_pc": 5, "comment": "Отличный курс!"},
            {"teacher_id": 2, "rating_pc": 4, "comment": 'Тест "кавычек"'}
        ]
        csv_data = CSVExporter.export_feedbacks(feedbacks)
        lines = csv_data.split("\n")
        self.assertEqual(lines[0], "teacher_id,rating_pc,comment")
        self.assertEqual(lines[1], '1,5,"Отличный курс!"')
        self.assertEqual(lines[2], '2,4,"Тест ""кавычек"""')

    def test_mime_database(self):
        self.assertEqual(ExpandedMimeDatabase.get("index.html"), "text/html")
        self.assertEqual(ExpandedMimeDatabase.get("styles.css"), "text/css")
        self.assertEqual(ExpandedMimeDatabase.get("app.js"), "application/javascript")
        self.assertEqual(ExpandedMimeDatabase.get("image.png"), "image/png")
        self.assertEqual(ExpandedMimeDatabase.get("unknown_file.xyz"), "application/octet-stream")

    def test_trie_router(self):
        router = TrieRouter()
        handler_root = lambda r: "root"
        handler_stats = lambda r: "stats"
        handler_teacher = lambda r: f"teacher_{r.path_params['id']}"
        
        router.add_route("/", "GET", handler_root)
        router.add_route("/api/stats", "GET", handler_stats)
        router.add_route("/api/teachers/<int:id>", "GET", handler_teacher)
        
        h1, params1 = router.resolve("/", "GET")
        self.assertIsNotNone(h1)
        self.assertEqual(h1(None), "root")
        
        h2, params2 = router.resolve("/api/stats", "GET")
        self.assertIsNotNone(h2)
        self.assertEqual(h2(None), "stats")
        
        h3, params3 = router.resolve("/api/teachers/42", "GET")
        self.assertIsNotNone(h3)
        self.assertEqual(params3["id"], 42)
        
        class MockRequest:
            def __init__(self, params):
                self.path_params = params
                
        self.assertEqual(h3(MockRequest(params3)), "teacher_42")

    def test_request_parsing(self):
        raw = b"GET /api/stats?filter=active HTTP/1.1\r\nHost: localhost\r\nCookie: session_id=abc123xyz\r\n\r\n"
        req = Request.parse(raw, ("127.0.0.1", 12345))
        self.assertEqual(req.method, "GET")
        self.assertEqual(req.path, "/api/stats")
        self.assertEqual(req.query_params["filter"], ["active"])
        self.assertEqual(req.headers["host"], "localhost")
        self.assertEqual(req.cookies["session_id"], "abc123xyz")

    def test_response_serialization(self):
        resp = Response(HTTPStatus.OK, {"Content-Type": "application/json"}, '{"status":"ok"}')
        serialized = resp.serialize()
        self.assertTrue(serialized.startswith(b"HTTP/1.1 200 OK\r\n"))
        self.assertTrue(b"Content-Type: application/json\r\n" in serialized)
        self.assertTrue(serialized.endswith(b'{"status":"ok"}'))

if __name__ == "__main__":
    unittest.main()
