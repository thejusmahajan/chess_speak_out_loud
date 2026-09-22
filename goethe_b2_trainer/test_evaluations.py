"""
Automated Verification Test for Goethe B2 Simulator.
Tests exam data integrity and Gemini evaluation pipelines.
"""

import sys
import os
from pathlib import Path

# Add project dir to path
PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))

from exam_data import EXAM_CONFIG, MODULE_CONTENT
from gemini_evaluator import evaluate_writing, evaluate_speaking, GEMINI_API_KEY


def test_exam_data():
    print(">>> Testing Exam Data Integrity...")
    assert "modules" in EXAM_CONFIG, "EXAM_CONFIG missing modules"
    assert len(EXAM_CONFIG["modules"]) == 4, "Must have 4 Goethe B2 modules"
    
    for mod_id in ["lesen", "hoeren", "schreiben", "sprechen"]:
        assert mod_id in MODULE_CONTENT, f"Missing content for module {mod_id}"
        print(f"  ✓ Module '{mod_id}' configured with title: {MODULE_CONTENT[mod_id]['title']}")
    print("  ✓ All 4 modules passed data validation.\n")


def test_writing_evaluation():
    print(">>> Testing Writing Evaluation with Gemini...")
    sample_text = (
        "In der heutigen Zeit ist das Thema verpackungsfreies Einkaufen von großer Bedeutung. "
        "Meiner Ansicht nach stellen unverpackte Lebensmittel einen wichtigen Schritt für den Umweltschutz dar. "
        "Ein wesentlicher Grund für die weite Verbreitung von Plastikverpackungen liegt in der langen Haltbarkeit "
        "und den geringen Transportkosten für die Supermärkte. Zwar bietet Plastik Hygiene, aber die ökologischen "
        "Folgen sind gravierend. Als Alternative könnten Konsumenten auf Wochenmärkten einkaufen oder wiederverwendbare "
        "Taschen und Gläser nutzen. Zusammenfassend lässt sich sagen, dass ein Umdenken dringend erforderlich ist."
    )
    prompt = MODULE_CONTENT["schreiben"]["prompt"]
    res = evaluate_writing(essay_text=sample_text, task_prompt=prompt)
    
    print(f"  Word Count: {res.get('word_count')}")
    print(f"  Total Score: {res.get('total_score')} / {res.get('max_score')}")
    print(f"  Percentage: {res.get('percentage')}%")
    print(f"  Passed: {res.get('passed')}")
    print(f"  CEFR Estimate: {res.get('cefr_level_estimate')}")
    if res.get("scores"):
        print(f"  Scores Breakdown: {res.get('scores')}")
    assert "total_score" in res, "Missing total_score in writing evaluation"
    print("  ✓ Writing evaluation succeeded.\n")


def test_speaking_audio_evaluation():
    print(">>> Testing Speaking Multimodal Audio Evaluation with Gemini...")
    wav_path = PROJECT_DIR / "content" / "audio" / "hoeren_sample.wav"
    if not wav_path.exists():
        print("  Generating test audio...")
        from app import ensure_sample_audio
        ensure_sample_audio()

    with open(wav_path, "rb") as f:
        audio_bytes = f.read()

    prompt = MODULE_CONTENT["sprechen"]["prompt"]
    res = evaluate_speaking(audio_bytes=audio_bytes, mime_type="audio/wav", task_prompt=prompt)
    
    print(f"  Spoken Transcript: {res.get('transcript')[:100]}...")
    print(f"  Total Score: {res.get('total_score')} / {res.get('max_score')}")
    print(f"  Passed: {res.get('passed')}")
    if res.get("scores"):
        print(f"  Scores Breakdown: {res.get('scores')}")
    if res.get("corrections"):
        print(f"  Sample Correction: {res.get('corrections')[:1]}")
    assert "total_score" in res, "Missing total_score in speaking evaluation"
    print("  ✓ Speaking multimodal audio evaluation succeeded.\n")


if __name__ == "__main__":
    print("==================================================")
    print("   Starting Goethe B2 Simulator Test Suite")
    print(f"   GEMINI_API_KEY Configured: {bool(GEMINI_API_KEY)}")
    print("==================================================\n")
    test_exam_data()
    test_writing_evaluation()
    test_speaking_audio_evaluation()
    print("==================================================")
    print("   All tests completed successfully!")
    print("==================================================")
