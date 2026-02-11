"""Automated tests for SpeakSmart CRUD API endpoints.

Run with:  python -m pytest tests/test_api.py -v
"""

import os
import sys
import json
import unittest
import tempfile

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class BaseTestCase(unittest.TestCase):
    """Base class that gives each test a fresh Flask test client & database."""

    def setUp(self):
        # Create a brand-new temp DB for *each* test method
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp_path = self._tmp.name
        self._tmp.close()

        # Patch config BEFORE creating the app
        import app.config as cfg
        cfg.Config.DATABASE_PATH = self._tmp_path

        from app import create_app
        self.app = create_app()
        self.client = self.app.test_client()

    def tearDown(self):
        try:
            os.unlink(self._tmp_path)
        except OSError:
            pass


class TestHealthCheck(BaseTestCase):
    def test_health(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "SpeakSmart")


# ── Languages CRUD ─────────────────────────────────────────────────────

class TestLanguages(BaseTestCase):

    def _create_language(self, name="English", code="en"):
        return self.client.post(
            "/api/languages",
            data=json.dumps({"name": name, "code": code}),
            content_type="application/json",
        )

    def test_create_language(self):
        res = self._create_language()
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertEqual(data["name"], "English")
        self.assertEqual(data["code"], "en")
        self.assertIn("id", data)

    def test_get_all_languages(self):
        self._create_language("English", "en")
        self._create_language("Spanish", "es")
        res = self.client.get("/api/languages")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["count"], 2)

    def test_get_language_by_id(self):
        create_res = self._create_language()
        lid = create_res.get_json()["id"]
        res = self.client.get(f"/api/languages/{lid}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["name"], "English")

    def test_get_language_not_found(self):
        res = self.client.get("/api/languages/9999")
        self.assertEqual(res.status_code, 404)

    def test_update_language(self):
        create_res = self._create_language()
        lid = create_res.get_json()["id"]
        res = self.client.put(
            f"/api/languages/{lid}",
            data=json.dumps({"name": "British English", "code": "en-gb"}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["name"], "British English")

    def test_delete_language(self):
        create_res = self._create_language()
        lid = create_res.get_json()["id"]
        res = self.client.delete(f"/api/languages/{lid}")
        self.assertEqual(res.status_code, 200)
        # Verify it's gone
        res2 = self.client.get(f"/api/languages/{lid}")
        self.assertEqual(res2.status_code, 404)

    def test_duplicate_language(self):
        self._create_language("English", "en")
        res = self._create_language("English", "en")
        self.assertEqual(res.status_code, 400)


# ── Translations CRUD ──────────────────────────────────────────────────

class TestTranslations(BaseTestCase):

    def _seed_languages(self):
        r1 = self.client.post(
            "/api/languages",
            data=json.dumps({"name": "English", "code": "en"}),
            content_type="application/json",
        )
        r2 = self.client.post(
            "/api/languages",
            data=json.dumps({"name": "Spanish", "code": "es"}),
            content_type="application/json",
        )
        self.lang1_id = r1.get_json()["id"]
        self.lang2_id = r2.get_json()["id"]

    def _create_translation(self):
        return self.client.post(
            "/api/translations",
            data=json.dumps({
                "source_language_id": self.lang1_id,
                "target_language_id": self.lang2_id,
                "source_text": "Hello",
                "translated_text": "Hola",
            }),
            content_type="application/json",
        )

    def test_create_translation(self):
        self._seed_languages()
        res = self._create_translation()
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertEqual(data["source_text"], "Hello")
        self.assertEqual(data["translated_text"], "Hola")

    def test_get_all_translations(self):
        self._seed_languages()
        self._create_translation()
        res = self.client.get("/api/translations")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["count"], 1)

    def test_get_translation_by_id(self):
        self._seed_languages()
        create_res = self._create_translation()
        tid = create_res.get_json()["id"]
        res = self.client.get(f"/api/translations/{tid}")
        self.assertEqual(res.status_code, 200)

    def test_update_translation(self):
        self._seed_languages()
        create_res = self._create_translation()
        tid = create_res.get_json()["id"]
        res = self.client.put(
            f"/api/translations/{tid}",
            data=json.dumps({"translated_text": "¡Hola!"}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["translated_text"], "¡Hola!")

    def test_delete_translation(self):
        self._seed_languages()
        create_res = self._create_translation()
        tid = create_res.get_json()["id"]
        res = self.client.delete(f"/api/translations/{tid}")
        self.assertEqual(res.status_code, 200)

    def test_create_translation_invalid_language(self):
        res = self.client.post(
            "/api/translations",
            data=json.dumps({
                "source_language_id": 999,
                "target_language_id": 888,
                "source_text": "Hi",
                "translated_text": "Hola",
            }),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 404)


# ── Grammar Rules CRUD ─────────────────────────────────────────────────

class TestGrammarRules(BaseTestCase):

    def _seed_language(self):
        r = self.client.post(
            "/api/languages",
            data=json.dumps({"name": "English", "code": "en"}),
            content_type="application/json",
        )
        self.lang_id = r.get_json()["id"]

    def _create_rule(self):
        return self.client.post(
            "/api/grammar-rules",
            data=json.dumps({
                "language_id": self.lang_id,
                "rule_name": "Subject-Verb Agreement",
                "description": "The subject and verb must agree in number.",
                "example_correct": "She runs every day.",
                "example_incorrect": "She run every day.",
            }),
            content_type="application/json",
        )

    def test_create_grammar_rule(self):
        self._seed_language()
        res = self._create_rule()
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertEqual(data["rule_name"], "Subject-Verb Agreement")

    def test_get_all_grammar_rules(self):
        self._seed_language()
        self._create_rule()
        res = self.client.get("/api/grammar-rules")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["count"], 1)

    def test_get_grammar_rule_by_id(self):
        self._seed_language()
        create_res = self._create_rule()
        rid = create_res.get_json()["id"]
        res = self.client.get(f"/api/grammar-rules/{rid}")
        self.assertEqual(res.status_code, 200)

    def test_update_grammar_rule(self):
        self._seed_language()
        create_res = self._create_rule()
        rid = create_res.get_json()["id"]
        res = self.client.put(
            f"/api/grammar-rules/{rid}",
            data=json.dumps({"description": "Updated description."}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["description"], "Updated description.")

    def test_delete_grammar_rule(self):
        self._seed_language()
        create_res = self._create_rule()
        rid = create_res.get_json()["id"]
        res = self.client.delete(f"/api/grammar-rules/{rid}")
        self.assertEqual(res.status_code, 200)


if __name__ == "__main__":
    unittest.main()
