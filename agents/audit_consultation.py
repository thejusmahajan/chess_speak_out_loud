#!/usr/bin/env python
"""Audit a Gemini consultation file's claims table.

The standing rule in this project is that a quote which does not grep is a
fabrication. This makes that check mechanical instead of manual, because the
leader is the bottleneck.

For every row of the claims table:
  VERIFIED    -> the cited file must exist and must contain the quoted text
  EXTERNAL    -> a full URL and a fetch date must be present
  INFERRED    -> at least one source must be cited
  UNVERIFIED  -> always passes, but is counted and listed

Usage:
    python agents/audit_consultation.py agents/consultations/2026-08-29_01_foo.md
    python agents/audit_consultation.py            # audits every UNAUDITED file
"""
import io
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONSULT_DIR = PROJECT_ROOT / "agents" / "consultations"

VALID_TAGS = {"VERIFIED", "INFERRED", "EXTERNAL", "UNVERIFIED"}


def normalise(text):
    """Collapse whitespace and smart quotes so quoting is robust to rewrapping."""
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("—", "-").replace("–", "-")
    return re.sub(r"\s+", " ", text).strip()


def parse_rows(md):
    """Yield (lineno, cells) for each data row of the claims table."""
    in_table = False
    for lineno, line in enumerate(md.splitlines(), 1):
        if re.match(r"^\s*\|\s*#\s*\|", line):
            in_table = True
            continue
        if in_table:
            if not line.strip().startswith("|"):
                in_table = False
                continue
            if re.match(r"^\s*\|[\s\-:|]+\|\s*$", line):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 5:
                yield lineno, cells


def audit(path):
    md = io.open(path, encoding="utf-8").read()
    md_norm = normalise(md)
    problems, counts = [], {t: 0 for t in VALID_TAGS}
    rows = list(parse_rows(md))

    if not rows:
        problems.append("NO CLAIMS TABLE FOUND - the answer is incomplete per CONSULT_GEMINI.md §5")

    for lineno, cells in rows:
        idx, claim, tag, source, quote = cells[0], cells[1], cells[2].upper(), cells[3], cells[4]
        if tag not in VALID_TAGS:
            problems.append(f"row {idx} (line {lineno}): unknown tag {cells[2]!r}")
            continue
        counts[tag] += 1

        if tag == "VERIFIED":
            m = re.search(r"`([^`]+?)`", source)
            if not m:
                problems.append(f"row {idx}: VERIFIED but no `path` in the source cell")
                continue
            rel = re.sub(r":\d+(-\d+)?$", "", m.group(1)).strip()
            target = PROJECT_ROOT / rel
            if not target.exists():
                problems.append(f"row {idx}: cited file does not exist -> {rel}")
                continue
            q = normalise(quote).strip('"').strip("'")
            if len(q) < 8:
                problems.append(f"row {idx}: quote too short to verify ({q!r})")
                continue
            try:
                body = normalise(io.open(target, encoding="utf-8", errors="replace").read())
            except Exception as e:                       # noqa: BLE001
                problems.append(f"row {idx}: could not read {rel}: {e}")
                continue
            if q not in body:
                problems.append(f"row {idx}: *** QUOTE NOT FOUND in {rel} *** -> {q[:90]!r}")

        elif tag == "EXTERNAL":
            if not re.search(r"https?://", source):
                problems.append(f"row {idx}: EXTERNAL but no URL in the source cell")
            if not re.search(r"\d{4}-\d{2}-\d{2}", source):
                problems.append(f"row {idx}: EXTERNAL but no fetch date in the source cell")

        elif tag == "INFERRED":
            if source.strip() in {"", "-", "--"}:
                problems.append(f"row {idx}: INFERRED but cites no source")

    # A claim tagged UNVERIFIED must not be restated as fact elsewhere in the prose.
    for lineno, cells in rows:
        if cells[2].upper() == "UNVERIFIED":
            key = normalise(cells[1])
            if len(key) > 25 and md_norm.count(key) > 1:
                problems.append(
                    f"row {cells[0]}: UNVERIFIED claim also appears in the prose - "
                    f"check it is not stated as fact there"
                )
    return rows, counts, problems


def main():
    targets = [Path(a) for a in sys.argv[1:]]
    if not targets:
        if not CONSULT_DIR.exists():
            print("no agents/consultations/ directory yet - nothing to audit")
            return 0
        # `_`-prefixed files are fixtures (see _selftest.md), never real consultations.
        targets = [p for p in sorted(CONSULT_DIR.glob("*.md"))
                   if not p.name.startswith("_")
                   and "Status:** UNAUDITED" in io.open(p, encoding="utf-8").read()]
        if not targets:
            print("no UNAUDITED consultations found")
            return 0

    failed = False
    for path in targets:
        rows, counts, problems = audit(path)
        print(f"\n=== {path} ===")
        print(f"  claims: {len(rows)}  " + "  ".join(f"{t}={counts[t]}" for t in sorted(counts)))
        if problems:
            failed = True
            print(f"  [FAIL] {len(problems)} problem(s):")
            for p in problems:
                print(f"    - {p}")
        else:
            print("  [PASS] every VERIFIED quote greps; every EXTERNAL has a URL and a date.")
        print("  NOTE: this checks sourcing, NOT whether the reasoning is right. Read it.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
