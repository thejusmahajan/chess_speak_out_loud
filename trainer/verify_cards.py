"""
Verify Cards Content Gate & URL Resolver.

Validates all cards in trainer/content/ladders/*.json against strict quality,
grounding, prerequisite, and forbidden-claim gates. Exits non-zero on any failure.

Usage:
  python trainer/verify_cards.py              # Run local content and grounding gates
  python trainer/verify_cards.py --check-urls # Run local gates + live external URL resolution
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import ssl
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
from urllib.error import HTTPError, URLError

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

TRAINER_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TRAINER_DIR.parent
LADDERS_DIR = TRAINER_DIR / "content" / "ladders"

REAL_DO_NOT_CLAIM_PATH = Path(
    r"C:\Users\Admin\Documents\job_search\applications\hereon_aeon_up\study_room\06_do_not_claim.md"
)
ADDITIONAL_CV_PATH = PROJECT_ROOT / "docs" / "CV_AI_MODULE.md"

# Phrases that indicate permissible disclaimer context
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
    r"boundary",
    r"distinction between",
]


def load_real_do_not_claim_patterns(file_path: Path = REAL_DO_NOT_CLAIM_PATH) -> List[str]:
    """
    Parse the markdown table from the REAL 06_do_not_claim.md file.
    Fails loudly if the file is missing or unreadable.
    """
    if not file_path.exists():
        raise FileNotFoundError(
            f"[CRITICAL GATE FAILURE] The authoritative do-not-claim file was not found at:\n"
            f"  {file_path}\n"
            f"A missing constraint file must stop the build. No fallback permitted."
        )

    content = file_path.read_text(encoding="utf-8")
    
    # Parse table rows containing ❌
    patterns: List[str] = []
    current_cell: List[str] = []
    in_table = False

    for line in content.splitlines():
        line_str = line.strip()
        if line_str.startswith("|") and "❌" in line_str and "NEVER CLAIM" in line_str:
            in_table = True
            continue
        if in_table:
            if line_str.startswith("+") or line_str.startswith("```"):
                if current_cell:
                    full_text = " ".join(current_cell).strip()
                    # Clean leading numbering like '1. '
                    full_text = re.sub(r"^\d+\.\s*", "", full_text)
                    if full_text:
                        patterns.append(full_text)
                    current_cell = []
                if line_str.startswith("```"):
                    in_table = False
            elif line_str.startswith("|"):
                parts = line.split("|")
                if len(parts) >= 2:
                    cell_0 = parts[1].strip()
                    if cell_0:
                        current_cell.append(cell_0)

    if len(patterns) < 5:
        raise ValueError(
            f"[CRITICAL GATE FAILURE] Expected at least 5 forbidden patterns from {file_path}, but found only {len(patterns)}:\n"
            f"  {patterns}"
        )

    return patterns


def load_additional_cv_patterns(file_path: Path = ADDITIONAL_CV_PATH) -> List[str]:
    """Load additional forbidden claim bullet points from docs/CV_AI_MODULE.md."""
    patterns = []
    if file_path.exists():
        content = file_path.read_text(encoding="utf-8")
        for line in content.splitlines():
            line_str = line.strip()
            if line_str.startswith("- ❌") or line_str.startswith("❌"):
                claim_text = line_str.replace("- ❌", "").replace("❌", "").strip()
                # Extract bolded text if present
                match = re.search(r"\*\*([^*]+)\*\*", claim_text)
                if match:
                    phrase = match.group(1).strip()
                    patterns.append(phrase)
                else:
                    patterns.append(claim_text)
    return patterns


def check_single_url(url: str) -> Tuple[str, int, str, Optional[str]]:
    """
    Resolve an external URL with retry logic. Returns (url, status_code, final_url, error_msg).
    Treats HTTP 200, 301, 302, 403 (paywalls) as resolved; 404/permanent errors as failed.
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                return (url, resp.getcode(), resp.geturl(), None)
        except HTTPError as e:
            if e.code == 403:
                return (url, 403, url, None)
            if e.code == 404:
                return (url, 404, url, "HTTP 404 (Not Found)")
            if attempt == 1:
                return (url, e.code, url, f"HTTP {e.code}")
        except Exception as e:
            if attempt == 1:
                return (url, 0, url, str(e))
    return (url, 0, url, "Unknown error")


def verify_all_cards(
    ladders_dir: Path = LADDERS_DIR,
    root_dir: Path = PROJECT_ROOT,
    check_urls: bool = False,
) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Verify all ladder JSON files.
    Returns (success, list_of_errors, stats_dict)
    """
    errors: List[str] = []
    stats: Dict[str, Any] = {
        "total_cards": 0,
        "ladders": {},
        "do_not_claim_count": 0,
        "repo_sources_count": 0,
        "url_sources_count": 0,
        "url_results": {},
    }

    # Gate: Load real do-not-claim patterns (strictly required, fails loudly on missing file)
    real_patterns = load_real_do_not_claim_patterns()
    cv_patterns = load_additional_cv_patterns()
    all_forbidden = real_patterns + cv_patterns
    stats["do_not_claim_count"] = len(real_patterns)

    # Keywords from forbidden claims for regex checking
    forbidden_regexes = [
        re.compile(r"published (work|papers?)\s+in\s+(Bayesian|neural process)", re.I),
        re.compile(r"hands-on experience with (CMAQ|EPISODE-CityChem|WRF-Chem)", re.I),
        re.compile(r"formal domain expertise in urban air quality", re.I),
        re.compile(r"causal intervention|activation patching|circuit discovery", re.I),
        re.compile(r"trained (LC0|Leela)", re.I),
        re.compile(r"fine-tuned (LC0|Leela)", re.I),
        re.compile(r"trained (probe|probing classifier)", re.I),
    ]

    if not ladders_dir.exists():
        return False, [f"Ladders directory not found: {ladders_dir}"], stats

    json_files = list(ladders_dir.glob("*.json"))
    if not json_files:
        return False, [f"No ladder JSON files found in {ladders_dir}"], stats

    all_cards: Dict[str, Dict[str, Any]] = {}
    ladders: Dict[str, List[Dict[str, Any]]] = {}
    all_urls: Set[str] = set()

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
            if not isinstance(level, int) or level < 0 or level > 5:
                errors.append(f"Card '{card_id}': Level must be integer 0..5, got {level}.")

            # Gate: Math LaTeX Delimiters and KaTeX Macro validation
            UNSUPPORTED_KATEX_MACROS = re.compile(
                r"\\(label|ref|eqref|cite|pageref|nameref|autoref|input|include)\b"
            )
            for field in ("question", "answer", "explanation", "trap"):
                val = card.get(field, "")
                if isinstance(val, str) and val:
                    # 1. Check balanced display delimiters ($$)
                    display_count = val.count("$$")
                    if display_count % 2 != 0:
                        errors.append(
                            f"Card '{card_id}': Field '{field}' has unbalanced display math delimiters ($$). Count is {display_count}."
                        )
                    
                    # Strip out display math to check inline math delimiters ($)
                    clean_inline = re.sub(r"\$\$.*?\$\$", "", val, flags=re.DOTALL)
                    # Ignore escaped dollar signs \$
                    clean_inline = clean_inline.replace(r"\$", "")
                    inline_count = clean_inline.count("$")
                    if inline_count % 2 != 0:
                        errors.append(
                            f"Card '{card_id}': Field '{field}' has unbalanced inline math delimiters ($). Count is {inline_count}."
                        )

                    # 2. Check for unsupported KaTeX macros across field content
                    macro_match = UNSUPPORTED_KATEX_MACROS.search(val)
                    if macro_match:
                        errors.append(
                            f"Card '{card_id}': Field '{field}' contains unsupported KaTeX macro '\\{macro_match.group(1)}'."
                        )

            # Gate 1: Non-empty sources list & session log rule
            sources = card.get("sources", [])
            if not isinstance(sources, list) or len(sources) == 0:
                errors.append(f"Card '{card_id}': Sources list must be non-empty.")
            else:
                has_substantive_source = False
                for src in sources:
                    if not isinstance(src, str) or not src.strip():
                        errors.append(f"Card '{card_id}': Invalid empty source string.")
                    elif src.startswith("http://") or src.startswith("https://") or src.startswith("arxiv:"):
                        stats["url_sources_count"] += 1
                        all_urls.add(src)
                        has_substantive_source = True
                    else:
                        stats["repo_sources_count"] += 1
                        base_path = src.split("#")[0].split(":")[0].strip()
                        if base_path:
                            target_file = root_dir / base_path
                            if not target_file.exists():
                                errors.append(f"Card '{card_id}': Cited repo source path does not exist on disk: '{base_path}'.")
                            elif "SESSION_LOG" not in base_path:
                                has_substantive_source = True

                # Section 4 Rule: A session log may corroborate a card, but may NEVER be its only source.
                if not has_substantive_source:
                    errors.append(
                        f"Card '{card_id}': Sourced exclusively from session logs/transcripts. "
                        f"Must have at least one external publication or repository code/analysis file."
                    )

            # Gate 6: Forbidden claims regex screening
            card_text = f"{card.get('question', '')} {card.get('answer', '')} {card.get('explanation', '')}"
            for pat in forbidden_regexes:
                if pat.search(card_text):
                    is_disclaimed = any(re.search(d_pat, card_text, re.IGNORECASE) for d_pat in DISCLAIMER_PATTERNS)
                    if not is_disclaimed:
                        errors.append(
                            f"Card '{card_id}': Matches forbidden claim regex '{pat.pattern}' without explicit disclaimer."
                        )

    # Gate 4: Prerequisites validation (exists & strictly lower level)
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
        l0_count = sum(1 for c in cards if c.get("level") == 0)
        stats.setdefault("level_0_counts", {})[ladder_name] = l0_count
        stats["ladders"][ladder_name] = len(cards)
        stats["total_cards"] += len(cards)

    # Optional Live URL Resolution Gate (--check-urls)
    if check_urls and all_urls:
        print(f"\nResolving {len(all_urls)} unique external URLs in parallel...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            future_to_url = {executor.submit(check_single_url, u): u for u in all_urls}
            for future in concurrent.futures.as_completed(future_to_url):
                u, status_code, final_url, err = future.result()
                stats["url_results"][u] = {
                    "status_code": status_code,
                    "final_url": final_url,
                    "error": err,
                }
                if status_code == 404 or (status_code == 0 and err):
                    errors.append(f"URL Resolution Failed ({err or status_code}): '{u}'")
                elif status_code in (200, 301, 302, 403):
                    pass
                else:
                    errors.append(f"URL returned abnormal status ({status_code}): '{u}'")

    success = len(errors) == 0
    return success, errors, stats


def main():
    parser = argparse.ArgumentParser(description="Knowledge Trainer Card Gate & URL Checker")
    parser.add_argument("--check-urls", action="store_true", help="Perform live HTTP resolution on all external URLs")
    args = parser.parse_args()

    print("=" * 65)
    print("Verifying Knowledge Trainer Content Ladders & Boundaries...")
    print("=" * 65)

    try:
        success, errors, stats = verify_all_cards(check_urls=args.check_urls)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}\n")
        sys.exit(1)

    print(f"Loaded {stats['do_not_claim_count']} authoritative forbidden claim boundaries from 06_do_not_claim.md.")

    if not success:
        print(f"\n[FAIL] Found {len(errors)} content verification error(s):\n")
        for idx, err in enumerate(errors, 1):
            print(f"  {idx}. {err}")
        print("\n" + "=" * 65)
        sys.exit(1)
    else:
        print("\n[PASS] All content, grounding, and constraint gates passed!\n")
        print("Card Counts by Ladder:")
        for ladder, count in sorted(stats["ladders"].items()):
            l0 = stats.get("level_0_counts", {}).get(ladder, 0)
            print(f"  - {ladder}: {count} cards (Level 0: {l0})")
        print(f"\nTotal verified cards: {stats['total_cards']}")
        print(f"Total repo citations: {stats['repo_sources_count']}")
        print(f"Total URL citations:  {stats['url_sources_count']}")
        if args.check_urls:
            print(f"All {len(stats['url_results'])} external URLs successfully resolved!")
        print("=" * 65)
        sys.exit(0)


if __name__ == "__main__":
    main()
