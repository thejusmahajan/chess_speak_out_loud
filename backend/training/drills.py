import datetime
import uuid
import chess
from backend.training import store, puzzle_db, metrics

async def generate_drill_set(count: int, profile: dict, repertoire: dict, engine, vision) -> dict:
    own_game_count = int(count * 0.4)
    corpus_count = int(count * 0.4)
    hidden_gem_count = count - own_game_count - corpus_count

    drills = []
    
    if profile and "findings" in profile:
        def sort_key(f):
            conf = f.get("confirmation", {})
            return (conf.get("confirmed", False), conf.get("swing_cp", 0))
            
        findings = sorted(profile["findings"], key=sort_key, reverse=True)
        
        for f in findings[:own_game_count]:
            board_before = chess.Board(f["fen_before"])
            epd = board_before.epd()
            policy_data = store.EpdCache("policy").get(epd)
            if policy_data and "policy" in policy_data:
                alt_ucis = metrics.alt_solutions(policy_data["policy"])
            else:
                alt_ucis = [f["best"]["uci"]]
            alt_ucis = sorted({u for a in alt_ucis
                               for u in metrics.accepted_ucis(board_before, a)})
                
            b_data = store.EpdCache("stage_b").get(epd)
            saliency = b_data["saliency"] if (b_data and "saliency" in b_data) else {}
                
            drills.append({
                "id": f"d-{uuid.uuid4().hex[:8]}",
                "source": "own_game",
                "fen": f["fen_before"],
                "setup_move_uci": None,
                "solution_uci": f["best"]["uci"],
                "alt_solution_ucis": alt_ucis,
                "solution_san": f["best"]["san"],
                "tags": f.get("motifs", []),
                "difficulty": 1500,
                "origin": {"finding_id": f["id"], "puzzle_id": None, "eco": f.get("opening", {}).get("eco")},
                "reveal": {
                    "policy": policy_data["policy"] if policy_data else [],
                    "saliency": saliency,
                    "motifs": f.get("motifs", []),
                    "concepts": f.get("concepts", []),
                    "pv_san": f.get("pv_san", []),
                    "swing_cp": f.get("confirmation", {}).get("swing_cp", 0)
                }
            })
            
    top_motifs = []
    if profile and "aggregates" in profile and "by_motif" in profile["aggregates"]:
        top_motifs = [m for m, stat in sorted(profile["aggregates"]["by_motif"].items(), key=lambda x: -x[1]["blind"])]
        
    puzzles = puzzle_db.sample_puzzles(top_motifs[:3] if top_motifs else None, None, (1600, 2300), corpus_count)
    
    for p in puzzles:
        moves = p["moves"].split()
        if len(moves) < 2:
            continue
        setup_move_uci = moves[0]
        solution_uci = moves[1]
        
        board = chess.Board(p["fen"])
        board.push_uci(setup_move_uci)
        fen_after_setup = board.fen()
        
        policy_dist = await engine.get_policy_distribution(fen_after_setup, nodes=1)
        saliency = vision.saliency_absolute(fen_after_setup)
        
        pv_san_list = []
        board_copy = board.copy()
        for m in moves[1:]:
            move = chess.Move.from_uci(m)
            pv_san_list.append(board_copy.san(move))
            board_copy.push(move)
        
        drills.append({
            "id": f"d-{uuid.uuid4().hex[:8]}",
            "source": "corpus",
            "fen": p["fen"],
            "setup_move_uci": setup_move_uci,
            "solution_uci": solution_uci,
            "alt_solution_ucis": metrics.accepted_ucis(board, solution_uci),
            "solution_san": board.san(chess.Move.from_uci(solution_uci)),
            "tags": p["themes"].split(),
            "difficulty": p["rating"],
            "origin": {"finding_id": None, "puzzle_id": p["id"], "eco": None},
            "reveal": {
                "policy": policy_dist,
                "saliency": saliency,
                "motifs": p["themes"].split(),
                "concepts": [],
                "pv_san": pv_san_list,
                "swing_cp": 0
            }
        })
        
    try:
        from backend.training.gems import scan_for_gems
        gems = await scan_for_gems(hidden_gem_count, profile, engine, vision)
    except ImportError:
        pass
        
    drill_set = {
        "id": f"set-{datetime.datetime.utcnow().strftime('%Y-%m-%d-%H%M%S')}-{uuid.uuid4().hex[:4]}",
        "created": datetime.datetime.utcnow().isoformat(),
        "drills": drills
    }
    store.save_drill_set(drill_set)
    return drill_set
