"""
Verify Cards Content Gate.

Validates all cards in trainer/content/ladders/*.json against strict quality,
grounding, prerequisite, and forbidden-claim gates. Exits non-zero on any failure.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

TRAINER_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TRAINER_DIR.parent
LADDERS_DIR = TRAINER_DIR / "content" / "ladders"

# Known forbidden claims fallback (from 06_do_not_claim.md / CV_AI_MODULE.md)
FORBIDDEN_CLAIM_PATTERNS = [
    r"published (work|papers?) in (Bayesian|neural process)",
    r"experience with (CMAQ|EPISODE-CityChem)",
    r"used (CMAQ|EPISODE-CityChem)",
    r"air quality domain experience",
    r"trained (LC0|Leela)",
    r"fine-tuned (LC0|Leela)",
    r"trained (probe|probing classifier)",
]

# Patterns that are allowed because they explicitly disclaim or describe limitation
DISCLAIMER_PATTERNS = [
    r"do not claim",
    r"must not claim",
    r"not yet",
    r"not ablate",
    r"no causal intervention",
    r"he has not",
    r"you do not",
    r"disclaimed",
    r"limitations?",
    r"future work",
]


def load_do_not_claim_patterns() -> List[str]:
    """Load forbidden patterns from 06_do_not_claim.md if accessible, or return defaults."""
    patterns = list(FORBIDDEN_CLAIM_PATTERNS)
    # Check potential locations
    paths = [
        Path(r"C:\Users\Admin\Documents\job_search\applications\hereon_aeon_up\study_room\06_do_not_claim.md"),
        PROJECT_ROOT / "docs" / "CV_AI_MODULE.md",
    ]
    for p in paths:
        if p.exists():
            try:
                content = p.read_text(encoding="utf-8")
                for line in content.splitlines():
                    if line.strip().startswith("- ❌") or line.strip().startswith("❌"):
                        claim_text = line.replace("- ❌", "").replace("❌", "").strip()
                        # Extract core phrase
                        match = re.search(r"\*\*([^*]+)\*\*", claim_text)
                        if match:
                            phrase = match.group(1).strip()
                            patterns.append(re.escape(phrase))
            except Exception:
                pass
    return list(set(patterns))


def verify_all_cards(ladders_dir: Path = LADDERS_DIR, root_dir: Path = PROJECT_ROOT) -> Tuple[bool, List[str]]:
    """
    Verify all ladder JSON files.
    
    Returns (success, list_of_errors)
    """
    errors: List[str] = []
    
    if not ladders_dir.exists():
        return False, [f"Ladders directory not found: {ladders_dir}"]
    
    json_files = list(ladders_dir.glob("*.json"))
    if not json_files:
        return False, [f"No ladder JSON files found in {ladders_dir}"]
    
    all_cards: Dict[str, Dict[str, Any]] = {}
    ladders: Dict[str, List[Dict[str, Any]]] = {}
    
    forbidden_patterns = load_do_not_claim_patterns()
    
    # 1. Load and check individual card structure & uniqueness
    for jf in json_files:
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            errors.append(f"Failed to parse JSON in {jf.name}: {e}")
            continue
        
        cards_list = data if isinstance(data, list) else data.get("cards", [])
        if not cards_list:
            errors.append(f"File {jf.name} contains no cards.")
            continue
        
        ladder_name = jf.stem
        ladders[ladder_name] = []
        
        for idx, card in enumerate(cards_list):
            card_id = card.get("id")
            if not card_id:
                errors.append(f"{jf.name} [card #{idx}]: Missing 'id'.")
                continue
            
            if card_id in all_cards:
                errors.append(f"Duplicate card ID '{card_id}' found in {jf.name} and {all_cards[card_id]['_file']}.")
            
            card["_file"] = jf.name
            all_cards[card_id] = card
            ladders[ladder_name].append(card)
            
            # Check required fields
            for req_field in ("id", "ladder", "level", "topic", "question", "answer", "sources", "difficulty", "requires"):
                if req_field not in card:
                    errors.append(f"Card '{card_id}': Missing required field '{req_field}'.")
            
            level = card.get("level")
            if not isinstance(level, int) or level < 1 or level > 5:
                errors.append(f"Card '{card_id}': Level must be integer 1..5, got {level}.")
                
            # Gate 1: Non-empty sources list
            sources = card.get("sources", [])
            if not isinstance(sources, list) or len(sources) == 0:
                errors.append(f"Card '{card_id}': Sources list must be non-empty.")
            else:
                for src in sources:
                    if not isinstance(src, str) or not src.strip():
                        errors.append(f"Card '{card_id}': Invalid empty source string.")
                    elif src.startswith("http://") or src.startswith("https://") or src.startswith("arxiv:"):
                        pass # Valid external URL / citation
                    else:
                        # Repo path check: e.g. "docs/writeup_attention_frame_bug.md#section" or "backend/neural_vision.py:130"
                        base_path = src.split("#")[0].split(":")[0].strip()
                        if base_path:
                            target_file = root_dir / base_path
                            if not target_file.exists():
                                errors.append(f"Card '{card_id}': Cited repo source path does not exist on disk: '{base_path}'.")
            
            # Gate 6: Check against forbidden claims in question/answer/explanation
            card_text = f"{card.get('question', '')} {card.get('answer', '')} {card.get('explanation', '')}"
            for pat in forbidden_patterns:
                if re.search(pat, card_text, re.IGNORECASE):
                    # Check if it is within a disclaimer
                    is_disclaimed = any(re.search(d_pat, card_text, re.IGNORECASE) for d_pat in DISCLAIMER_PATTERNS)
                    if not is_disclaimed:
                        errors.append(f"Card '{card_id}': Matches forbidden claim pattern '{pat}' without explicit disclaimer.")
    
    # Gate 4: Prerequisites validation (exists & level < card.level)
    for card_id, card in all_cards.items():
        reqs = card.get("requires", [])
        card_level = card.get("level", 1)
        for req_id in reqs:
            if req_id not in all_cards:
                errors.append(f"Card '{card_id}': Requires non-existent card '{req_id}'.")
            else:
                req_card = all_cards[req_id]
                req_level = req_card.get("level", 1)
                if req_level >= card_level:
                    errors.append(
                        f"Card '{card_id}' (level {card_level}): Requires card '{req_id}' of level {req_level} "
                        f"(requires must be lower level, strictly < {card_level})."
                    )
    
    # Gate 5: Every ladder has at least one level-5 card
    for ladder_name, cards in ladders.items():
        has_l5 = any(c.get("level") == 5 for c in cards)
        if not has_l5:
            errors.append(f"Ladder '{ladder_name}' has no level-5 card (must have at least one).")
            
    success = len(errors) == 0
    return success, errors


def main():
    print("=" * 60)
    print("Verifying Knowledge Trainer Content Ladders...")
    print("=" * 60)
    
    success, errors = verify_all_cards()
    
    if not success:
        print(f"\n[FAIL] Found {len(errors)} content verification error(s):\n")
        for idx, err in enumerate(errors, 1):
            print(f"  {idx}. {err}")
        print("\n" + "=" * 60)
        sys.exit(1)
    else:
        # Print summary
        ladders = list(LADDERS_DIR.glob("*.json"))
        total_cards = 0
        print("\n[PASS] All content gates passed successfully!\n")
        for jf in sorted(ladders):
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
                c_list = data if isinstance(data, list) else data.get("cards", [])
                total_cards += len(c_list)
                print(f"  - {jf.stem}: {len(c_list)} cards")
        print(f"\nTotal verified cards: {total_cards}")
        print("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    main()
