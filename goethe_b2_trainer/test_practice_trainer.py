"""
Unit and Integration Tests for Goethe B2 Practice Trainer.
Tests data models, sanitization, evaluation logic, and FastAPI endpoints.
"""

import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app import app
from practice_data import (
    PRACTICE_TIERS,
    PRACTICE_QUESTIONS,
    sanitize_for_client,
    evaluate_objective_question,
)


class TestPracticeTrainerBackend(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_tiers_and_questions_count(self):
        self.assertEqual(len(PRACTICE_TIERS), 3)
        self.assertEqual(len(PRACTICE_QUESTIONS), 10)
        
        simple_qs = [q for q in PRACTICE_QUESTIONS.values() if q["tier"] == "simple"]
        inter_qs = [q for q in PRACTICE_QUESTIONS.values() if q["tier"] == "intermediate"]
        diff_qs = [q for q in PRACTICE_QUESTIONS.values() if q["tier"] == "difficult"]
        
        self.assertEqual(len(simple_qs), 4)
        self.assertEqual(len(inter_qs), 4)
        self.assertEqual(len(diff_qs), 2)

    def test_client_sanitization(self):
        for q_id, q_data in PRACTICE_QUESTIONS.items():
            sanitized = sanitize_for_client(q_data)
            self.assertNotIn("accepted_answers", sanitized)
            self.assertNotIn("correct_pairs", sanitized)
            self.assertNotIn("correct_selection", sanitized)
            if q_data["type"] == "match_multiple":
                for opt in sanitized.get("options", []):
                    self.assertNotIn("is_correct", opt)
            if q_data["type"] == "find_mistake":
                for w in sanitized.get("sentence_words", []):
                    self.assertNotIn("is_error", w)

    def test_q1_fill_blank_single(self):
        # Correct answer
        res_correct = evaluate_objective_question("q1_simple_fill_single", "auf")
        self.assertTrue(res_correct["is_correct"])
        self.assertEqual(res_correct["score"], 10)
        
        # Incorrect answer
        res_wrong = evaluate_objective_question("q1_simple_fill_single", "über")
        self.assertFalse(res_wrong["is_correct"])
        self.assertEqual(res_wrong["score"], 0)

    def test_q2_match_following(self):
        # Correct pairs
        correct_pairs = {"L1": "R1", "L2": "R2", "L3": "R3", "L4": "R4"}
        res = evaluate_objective_question("q2_simple_match_following", correct_pairs)
        self.assertTrue(res["is_correct"])
        self.assertEqual(res["score"], 10)
        
        # Partial pairs
        partial_pairs = {"L1": "R1", "L2": "R2", "L3": "R1", "L4": "R3"}
        res_part = evaluate_objective_question("q2_simple_match_following", partial_pairs)
        self.assertFalse(res_part["is_correct"])
        self.assertEqual(res_part["matches_correct"], 2)

    def test_q3_odd_one_out(self):
        res = evaluate_objective_question("q3_simple_odd_one_out", "D")
        self.assertTrue(res["is_correct"])
        self.assertEqual(res["score"], 10)

        res_wrong = evaluate_objective_question("q3_simple_odd_one_out", "A")
        self.assertFalse(res_wrong["is_correct"])

    def test_q4_incorrect_spelling(self):
        res = evaluate_objective_question("q4_simple_incorrect_spelling", "B")
        self.assertTrue(res["is_correct"])
        self.assertEqual(res["score"], 10)

    def test_q5_fill_blank_multi(self):
        # Correct
        res = evaluate_objective_question("q5_inter_fill_multi", {
            "blank1": "nicht nur",
            "blank2": "sondern auch"
        })
        self.assertTrue(res["is_correct"])
        self.assertEqual(res["score"], 10)

        # Incorrect
        res_wrong = evaluate_objective_question("q5_inter_fill_multi", {
            "blank1": "entweder",
            "blank2": "oder"
        })
        self.assertFalse(res_wrong["is_correct"])

    def test_q6_match_multiple(self):
        # Correct exact selection: A, B, D
        res = evaluate_objective_question("q6_inter_match_multiple", ["A", "B", "D"])
        self.assertTrue(res["is_correct"])
        self.assertEqual(res["score"], 10)

        # Selection with wrong item
        res_wrong = evaluate_objective_question("q6_inter_match_multiple", ["A", "C"])
        self.assertFalse(res_wrong["is_correct"])

    def test_q7_jumbled_sentence(self):
        target = "Obwohl die Preise kontinuierlich steigen, verzichten die meisten Verbraucher nicht auf hochwertige Bio-Produkte."
        res = evaluate_objective_question("q7_inter_jumbled_sentence", target)
        self.assertTrue(res["is_correct"])
        self.assertEqual(res["score"], 10)

    def test_q8_find_mistake(self):
        res = evaluate_objective_question("q8_inter_find_mistake", {
            "selected_word": "dessen",
            "correction": "deren"
        })
        self.assertTrue(res["is_correct"])
        self.assertEqual(res["score"], 10)

    def test_api_categories_endpoint(self):
        resp = self.client.get("/api/practice/categories")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data["tiers"]), 3)
        self.assertEqual(data["total_questions"], 10)

    def test_api_questions_endpoint(self):
        resp = self.client.get("/api/practice/questions")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["total"], 10)
        self.assertEqual(len(data["questions"]), 10)

    def test_api_evaluate_objective(self):
        resp = self.client.post("/api/practice/evaluate", json={
            "question_id": "q1_simple_fill_single",
            "submission": "auf"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["is_correct"])
        self.assertEqual(data["score"], 10)

    def test_api_evaluate_difficult_q9(self):
        resp = self.client.post("/api/practice/evaluate", json={
            "question_id": "q9_diff_answer_question",
            "submission": "Arbeitspsychologen betonen, dass Jobsharing einen kontinuierlichen Kommunikationsaufwand erfordert. Andernfalls drohen gravierende Informationsverluste und Verzögerungen bei Entscheidungen."
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("score", data)
        self.assertIn("feedback", data)
        self.assertIn("model_answer", data)
        self.assertGreaterEqual(data["score"], 6)

    def test_api_evaluate_difficult_q10(self):
        resp = self.client.post("/api/practice/evaluate", json={
            "question_id": "q10_diff_write_next_sentence",
            "submission": "Andererseits birgt diese Flexibilität die Gefahr einer Entgrenzung der Arbeitszeit, da viele Beschäftigte auch nach Feierabend dienstliche Nachrichten beantworten."
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("score", data)
        self.assertIn("feedback", data)
        self.assertIn("model_answer", data)
        self.assertGreaterEqual(data["score"], 6)


if __name__ == "__main__":
    unittest.main()
