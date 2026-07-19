import io
import asyncio
import datetime
from collections import defaultdict
import chess
import chess.pgn
from backend.training import store, openings, metrics
from backend.tactics import MotifDetector
from backend.concept_mapper import analyze_position

async def run_diagnosis(job_id: str, pgn_text: str, player_name: str, engine, vision):
    try:
        store.update_job(job_id, status="running")
        
        policy_cache = store.EpdCache("policy")
        stage_b_cache = store.EpdCache("stage_b")
        
        pgn_io = io.StringIO(pgn_text)
        games_to_process = []
        all_players = set()
        
        # 1. Split multi-game PGN
        while True:
            game = chess.pgn.read_game(pgn_io)
            if game is None:
                break
                
            white = game.headers.get("White", "")
            black = game.headers.get("Black", "")
            
            if white and white != "?": all_players.add(white)
            if black and black != "?": all_players.add(black)
            
            user_color = None
            if player_name.lower() in white.lower():
                user_color = chess.WHITE
            elif player_name.lower() in black.lower():
                user_color = chess.BLACK
                
            if user_color is not None:
                games_to_process.append((game, user_color))

        if not games_to_process:
            players_str = ", ".join(sorted(list(all_players))) if all_players else "None"
            store.update_job(job_id, status="error", error=f"No games matched player '{player_name}'. Players in this PGN: {players_str}")
            return
                
        user_moves_count = 0
        for game, color in games_to_process:
            board = game.board()
            for move in game.mainline_moves():
                if board.turn == color:
                    user_moves_count += 1
                board.push(move)
                
        store.update_job(job_id, progress={"total": user_moves_count})
        
        findings = []
        moves_processed = 0
        flagged_count = 0
        games_analyzed = len(games_to_process)
        
        flagged_moves = []
        
        # STAGE A
        for game_idx, (game, user_color) in enumerate(games_to_process):
            board = game.board()
            ply = 0
            uci_moves = []
            
            for move in game.mainline_moves():
                ply += 1
                uci_moves.append(move.uci())
                
                if board.turn == user_color:
                    epd = board.epd()
                    
                    policy_data = policy_cache.get(epd)
                    if policy_data is None:
                        dist = await engine.get_policy_distribution(board.fen(), nodes=1)
                        if not dist:
                            raise Exception("engine in mock mode")
                        policy_data = {"policy": dist}
                        policy_cache.put(epd, policy_data)
                        
                    policy = policy_data["policy"]
                    div = metrics.policy_divergence(policy, metrics.policy_uci(board, move))
                    
                    if div and div["severity"] is not None:
                        flagged_moves.append({
                            "game_idx": game_idx,
                            "game": game,
                            "user_color": "white" if user_color == chess.WHITE else "black",
                            "ply": ply,
                            "move_number": (ply + 1) // 2,
                            "fen_before": board.fen(),
                            "epd": epd,
                            "played_move": move,
                            "played_uci": move.uci(),
                            "played_san": board.san(move),
                            "best_uci": div["best_uci"],
                            "best_san": div["best_san"],
                            "p_played": div["p_played"],
                            "p_best": div["p_best"],
                            "divergence": div["divergence"],
                            "severity": div["severity"],
                            "uci_moves_so_far": list(uci_moves)
                        })
                        flagged_count += 1
                        
                    moves_processed += 1
                    if moves_processed % 20 == 0:
                        store.update_job(job_id, progress={"stage_a_done": moves_processed, "flagged": flagged_count})
                        
                board.push(move)
                
        store.update_job(job_id, progress={"stage_a_done": moves_processed, "flagged": flagged_count})
        
        # STAGE B
        stage_b_done = 0
        for flagged in flagged_moves:
            epd = flagged["epd"]
            board_before = chess.Board(flagged["fen_before"])
            played_move = flagged["played_move"]
            
            b_data = stage_b_cache.get(epd)
            if b_data is None:
                b_data = {}
                analysis_before = await engine.analyze(flagged["fen_before"], depth=None, multipv=2, time_limit=3.0)
                b_data["eval_best_cp"] = analysis_before["evaluation"]
                b_data["pv_lines"] = analysis_before["pv_lines"]
                
                board_after = board_before.copy()
                board_after.push(played_move)
                analysis_after = await engine.analyze(board_after.fen(), depth=None, multipv=1, time_limit=1.5)
                b_data["eval_played_cp"] = analysis_after["evaluation"]
                
                saliency = vision.saliency_absolute(flagged["fen_before"])
                b_data["saliency"] = saliency
                
                pv_san_list = analysis_before["pv_lines"][0].split() if analysis_before["pv_lines"] else []
                b_data["pv_san_list"] = pv_san_list
                b_data["motifs"] = list(MotifDetector.analyze_pv(flagged["fen_before"], pv_san_list))
                b_data["concepts"] = analyze_position(flagged["fen_before"], analysis_before)
                
                stage_b_cache.put(epd, b_data)
                
            mover_is_white = (flagged["user_color"] == "white")
            conf = metrics.confirmation_swing(b_data["eval_best_cp"], b_data["eval_played_cp"], mover_is_white)
            if not conf:
                conf = {"swing_cp": 0, "confirmed": False}
                
            best_move = board_before.parse_uci(flagged["best_uci"])
            att = metrics.attention_blindness(b_data["saliency"], board_before, played_move, best_move)
            
            opening_match = openings.classify(flagged["uci_moves_so_far"])
            if opening_match:
                opening_data = {"eco": opening_match["eco"], "name": opening_match["name"]}
            else:
                opening_data = {"eco": "???", "name": "Unknown"}
                
            finding_id = f"g{flagged['game_idx']:03d}-p{flagged['ply']:03d}"
            headers = flagged["game"].headers
            
            finding = {
                "id": finding_id,
                "game": {
                    "white": headers.get("White", "?"),
                    "black": headers.get("Black", "?"),
                    "date": headers.get("Date", "?"),
                    "result": headers.get("Result", "?")
                },
                "user_color": flagged["user_color"],
                "ply": flagged["ply"],
                "move_number": flagged["move_number"],
                "fen_before": flagged["fen_before"],
                "played": {"uci": flagged["played_uci"], "san": flagged["played_san"], "p": flagged["p_played"]},
                "best": {"uci": flagged["best_uci"], "san": flagged["best_san"], "p": flagged["p_best"]},
                "divergence": flagged["divergence"],
                "severity": flagged["severity"],
                "attention": att,
                "confirmation": conf,
                "motifs": b_data["motifs"],
                "concepts": [obs["category"] for obs in b_data["concepts"].get("observations", [])] if isinstance(b_data["concepts"], dict) else [],
                "opening": opening_data,
                "pv_san": b_data["pv_san_list"]
            }
            findings.append(finding)
            
            stage_b_done += 1
            store.update_job(job_id, progress={"stage_b_done": stage_b_done})
            
        # Aggregate
        by_motif = defaultdict(lambda: {"missed": 0, "blind": 0, "confirmed": 0})
        by_opening = defaultdict(lambda: {"moves": 0, "missed": 0, "blind": 0, "blind_rate": 0.0})
        by_concept = defaultdict(lambda: {"missed": 0})
        
        intuitive_blind_count = 0
        attention_blind_count = 0
        
        for game_idx, (game, user_color) in enumerate(games_to_process):
            board = game.board()
            uci_moves = []
            for move in game.mainline_moves():
                uci_moves.append(move.uci())
                if board.turn == user_color:
                    opening_match = openings.classify(uci_moves)
                    if opening_match:
                        by_opening[opening_match["eco"]]["moves"] += 1
                board.push(move)
                
        for f in findings:
            weight = 2 if f["confirmation"].get("confirmed") else 1
            sev = f["severity"]
            
            if sev == "blind":
                intuitive_blind_count += 1
            if f["attention"].get("blind"):
                attention_blind_count += 1
                
            for m in f["motifs"]:
                by_motif[m][sev] += weight
                if f["confirmation"].get("confirmed"):
                    by_motif[m]["confirmed"] += 1
                    
            eco = f["opening"]["eco"]
            by_opening[eco][sev] += weight
            
            for c in f["concepts"]:
                by_concept[c]["missed"] += weight
                
        for eco, st in by_opening.items():
            if st["moves"] > 0:
                st["blind_rate"] = st["blind"] / st["moves"]
                
        aggregates = {
            "by_motif": {k: dict(v) for k, v in by_motif.items()},
            "by_opening": {k: dict(v) for k, v in by_opening.items()},
            "by_concept": {k: dict(v) for k, v in by_concept.items()},
            "intuitive_blindness_rate": intuitive_blind_count / max(1, moves_processed),
            "attention_blindness_rate": attention_blind_count / max(1, moves_processed)
        }
        
        profile = {
            "version": 1,
            "created": datetime.datetime.utcnow().isoformat(),
            "games_analyzed": games_analyzed,
            "moves_analyzed": moves_processed,
            "findings": findings,
            "aggregates": aggregates
        }
        
        from backend.training import attempts
        profile["regressions"] = attempts.escalate_regressions(profile)

        store.save_profile(profile)
        store.update_job(job_id, status="done")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        store.update_job(job_id, status="error", error=str(e))
