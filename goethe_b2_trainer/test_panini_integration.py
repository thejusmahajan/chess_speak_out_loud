"""
Integration tests for Pāṇini-Kanon B1 → B2 Curriculum Endpoints & Logic.
"""

import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from fastapi.testclient import TestClient
from app import app
import panini_data

class TestPaniniIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_panini_overview(self):
        res = self.client.get("/api/panini/overview")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("counts", data)
        self.assertEqual(data["counts"]["sutras"], 22)
        self.assertEqual(data["counts"]["lists"], 6)
        self.assertEqual(data["counts"]["transformations"], 13)
        self.assertEqual(data["counts"]["error_hunt"], 10)
        self.assertEqual(data["counts"]["translations"], 6)
        self.assertEqual(data["counts"]["topics"], 11)

    def test_panini_today(self):
        res = self.client.get("/api/panini/today")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("week", data)
        self.assertIn("day", data)
        self.assertIn("active_sutra", data)
        self.assertIn("transformation_drill", data)
        self.assertIn("checklist", data)

    def test_panini_sutras_and_filter(self):
        # All sūtras
        res = self.client.get("/api/panini/sutras")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total"], 22)

        # Filter by week
        res_w1 = self.client.get("/api/panini/sutras?week=1")
        self.assertEqual(res_w1.status_code, 200)
        data_w1 = res_w1.json()
        self.assertTrue(len(data_w1["sutras"]) >= 3)

        # Filter by adhyaya
        res_a1 = self.client.get("/api/panini/sutras?adhyaya=I")
        self.assertEqual(res_a1.status_code, 200)
        data_a1 = res_a1.json()
        self.assertEqual(len(data_a1["sutras"]), 3)

    def test_panini_single_sutra(self):
        res = self.client.get("/api/panini/sutra/sutra_01")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["sutra"]["number"], 1)
        self.assertEqual(data["sutra"]["title"], "Das Präpositionalobjekt")

    def test_panini_lists_and_flashcards(self):
        res = self.client.get("/api/panini/lists")
        self.assertEqual(res.status_code, 200)
        lists = res.json()
        self.assertEqual(len(lists), 6)
        self.assertIn("list_1", lists)
        self.assertIn("list_6", lists)

        res_fc = self.client.get("/api/panini/flashcards")
        self.assertEqual(res_fc.status_code, 200)
        fc_data = res_fc.json()
        self.assertGreater(fc_data["total"], 300)

    def test_panini_transformations(self):
        res = self.client.get("/api/panini/transformations")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["transformations"]), 13)
        self.assertEqual(len(data["nominalstil_matrix"]), 8)

    def test_panini_progress_actions(self):
        # Mark sūtra mastered
        res = self.client.post("/api/panini/progress", json={
            "action": "mark_sutra_mastered",
            "data": {"sutra_id": "sutra_01"}
        })
        self.assertEqual(res.status_code, 200)
        prog = res.json()
        self.assertIn("sutra_01", prog["sutras_mastered"])

        # Update checklist item
        res_chk = self.client.post("/api/panini/progress", json={
            "action": "update_checklist",
            "data": {"item_id": "sutras", "completed": True}
        })
        self.assertEqual(res_chk.status_code, 200)

    def test_evaluate_sakha_endpoint(self):
        res = self.client.post("/api/panini/evaluate-sakha", json={
            "sutra_id": "sutra_01",
            "user_text": "Ich interessiere mich sehr für moderne Datenanalyse und künstliche Intelligenz."
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["is_correct"])
        self.assertGreaterEqual(data["score"], 6)
        self.assertIn("feedback", data)

    def test_evaluate_transformation_endpoint(self):
        res = self.client.post("/api/panini/evaluate-transformation", json={
            "id": "I.1",
            "direction": "schlicht_to_gehoben",
            "user_text": "Nach eingehender Prüfung sämtlicher Unterlagen hat die Geschäftsleitung den Entschluss gefasst."
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("score", data)
        self.assertIn("target_model", data)

    def test_evaluate_error_hunt_endpoint(self):
        res = self.client.post("/api/panini/evaluate-error-hunt", json={
            "id": "II.1.1",
            "user_correction": "Nach eingehender Prüfung",
            "sutra_identified": "20"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("score", data)
        self.assertIn("official_correction", data)

if __name__ == "__main__":
    unittest.main()
