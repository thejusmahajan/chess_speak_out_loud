import os
import csv
import chess
from typing import List, Dict, Optional

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OPENINGS_DIR = os.getenv("CSZERO_OPENINGS_DIR", os.path.join(ROOT_DIR, "data", "openings"))

_openings_trie = {}  # tuple(uci) -> {"eco": str, "name": str}
_tabiya_fens = {}    # (eco, name) -> fen
_loaded = False

def to_opening_tag(name: str) -> str:
    """e.g. 'Sicilian Defense: Najdorf Variation' -> 'Sicilian_Defense_Najdorf_Variation'"""
    # We know lichess typically translates characters like this.
    tag = name.replace(":", "").replace(",", "").replace(".", "").replace("'", "")
    tag = tag.replace("-", " ")
    while "  " in tag:
        tag = tag.replace("  ", " ")
    return tag.strip().replace(" ", "_")

def _load_openings():
    global _loaded
    if _loaded:
        return
        
    if not os.path.exists(OPENINGS_DIR):
        _loaded = True
        return
        
    for letter in 'abcde':
        path = os.path.join(OPENINGS_DIR, f"{letter}.tsv")
        if not os.path.exists(path):
            continue
            
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            header = next(reader, None)
            if not header: continue
            
            for row in reader:
                if len(row) < 3: continue
                eco, name, pgn = row[0], row[1], row[2]
                
                board = chess.Board()
                uci_moves = []
                try:
                    for san_move in pgn.split():
                        if "." in san_move:
                            parts = san_move.split(".")
                            if len(parts) > 1 and parts[1]:
                                san_move = parts[1]
                            else:
                                continue
                                
                        move = board.parse_san(san_move)
                        uci_moves.append(move.uci())
                        board.push(move)
                        
                    seq = tuple(uci_moves)
                    # For longest-prefix matching, we just store exact sequence mappings.
                    # Since multiple ECOs might map to the same sequence (rare but possible), we keep the latest or whatever is in the DB.
                    _openings_trie[seq] = {"eco": eco, "name": name}
                    _tabiya_fens[(eco, name)] = board.fen()
                except Exception:
                    pass
                    
    _loaded = True

def classify(uci_moves: List[str]) -> Optional[Dict[str, str]]:
    """Longest prefix match for the given sequence of UCI moves."""
    _load_openings()
    
    # Try longest prefixes first
    for i in range(len(uci_moves), 0, -1):
        prefix = tuple(uci_moves[:i])
        if prefix in _openings_trie:
            return _openings_trie[prefix]
            
    return None

def tabiya_fen(eco: str, name: str) -> Optional[str]:
    _load_openings()
    return _tabiya_fens.get((eco, name))

def lines_by_tag() -> Dict[str, Dict]:
    """opening_tag -> {"eco","name","uci_moves","fen"}, keeping the shortest
    (defining) line per tag. Read-only accessor added for C2 repertoire
    selection (leader addition, logged in WORKLOG_TRAINING.md)."""
    _load_openings()
    result: Dict[str, Dict] = {}
    for seq, info in _openings_trie.items():
        tag = to_opening_tag(info["name"])
        current = result.get(tag)
        if current is None or len(seq) < len(current["uci_moves"]):
            # Recompute the fen from THIS line's moves — _tabiya_fens keys on
            # (eco, name), which duplicate names overwrite, so its fen may
            # belong to a different (deeper) line than the shortest one.
            board = chess.Board()
            try:
                for uci in seq:
                    board.push_uci(uci)
            except ValueError:
                continue
            result[tag] = {
                "eco": info["eco"],
                "name": info["name"],
                "uci_moves": list(seq),
                "fen": board.fen(),
            }
    return result
