import io
import re
import asyncio
import datetime
from collections import defaultdict
from typing import Optional
import chess
import chess.pgn
from backend.training import store, openings, metrics
from backend.tactics import MotifDetector
from backend.concept_mapper import analyze_position

_CLK_RE = re.compile(r"\[%clk\s+(\d+):(\d+):(\d+(?:\.\d+)?)\]")


def clock_seconds(comment: str) -> Optional[float]:
    """Seconds left on the mover's clock, read from a lichess-style
    [%clk H:MM:SS] annotation. None when the comment carries no clock."""
    m = _CLK_RE.search(comment or "")
    if not m:
        return None
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def is_time_scramble(comment: str,
                     cfg: metrics.TrainingConfig = metrics.DEFAULT_CONFIG) -> bool:
    """True when the move was played in a time scramble (clock below
    cfg.min_clock_seconds). Moves without clock data never count as
    scrambles, so PGNs without [%clk] are analyzed in full."""
    secs = clock_seconds(comment)
    return secs is not None and secs < cfg.min_clock_seconds


def _progress(job_id: str, **prog):
    """Best-effort progress ping. Progress is cosmetic — a locked job file
    (antivirus scan, concurrent poll) must never abort a multi-hour run.
    Status transitions still go through store.update_job directly and raise."""
    try:
        store.update_job(job_id, progress=prog)
    except OSError:
        pass

async def run_diagnosis(job_id: str, pgn_text: str, player_name: str, engine, vision):
    try:
        store.update_job(job_id, status="running")
        
        policy_cache = store.EpdCache("policy")
        stage_b_cache = store.EpdCache("stage_b")
        steer_cache = store.EpdCache("steer")
        
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
        scramble_skipped = 0
        for game, color in games_to_process:
            board = game.board()
            for node in game.mainline():
                if board.turn == color:
                    if is_time_scramble(node.comment):
                        scramble_skipped += 1
                    else:
                        user_moves_count += 1
                board.push(node.move)

        _progress(job_id, total=user_moves_count,
                  time_scramble_skipped=scramble_skipped)
        
        findings = []
        moves_processed = 0
        flagged_count = 0
        games_analyzed = len(games_to_process)
        
        flagged_moves = []
        user_decision_nodes = []
        
        # STAGE A
        for game_idx, (game, user_color) in enumerate(games_to_process):
            board = game.board()
            ply = 0
            uci_moves = []

            for node in game.mainline():
                move = node.move
                ply += 1
                uci_moves.append(move.uci())

                if board.turn == user_color and not is_time_scramble(node.comment):
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
                        
                    user_decision_nodes.append({
                        "game_idx": game_idx,
                        "game": game,
                        "ply": ply,
                        "user_color": user_color,
                        "fen_before": board.fen(),
                        "epd": epd,
                        "uci_moves_so_far": list(uci_moves)
                    })
                        
                    moves_processed += 1
                    if moves_processed % 20 == 0:
                        _progress(job_id, stage_a_done=moves_processed, flagged=flagged_count)
                        
                board.push(move)
                
        _progress(job_id, stage_a_done=moves_processed, flagged=flagged_count)

        # STAGE B
        stage_b_done = 0
        for flagged in flagged_moves:
            epd = flagged["epd"]
            board_before = chess.Board(flagged["fen_before"])
            played_move = flagged["played_move"]
            
            b_data = stage_b_cache.get(epd)
            if b_data is None:
                b_data = {}
                analysis_before = await engine.analyze(
                    flagged["fen_before"], depth=None, multipv=2,
                    time_limit=metrics.DEFAULT_CONFIG.confirm_best_seconds)
                b_data["eval_best_cp"] = analysis_before["evaluation"]
                b_data["pv_lines"] = analysis_before["pv_lines"]
                
                board_after = board_before.copy()
                board_after.push(played_move)
                analysis_after = await engine.analyze(
                    board_after.fen(), depth=None, multipv=1,
                    time_limit=metrics.DEFAULT_CONFIG.confirm_played_seconds)
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
            _progress(job_id, stage_b_done=stage_b_done)
            
        # STAGE TS2: Steering Pass
        steer_findings = []
        by_opening_steer = defaultdict(lambda: {"moves": 0, "complexity_sum": 0.0, "tal_moves": 0})
        bt3_budget_remaining = metrics.DEFAULT_CONFIG.steer_bt3_budget
        steer_processed = 0

        for node in user_decision_nodes:
            epd = node["epd"]
            fen_before = node["fen_before"]
            user_color = node["user_color"]
            board_before = chess.Board(fen_before)
            
            policy_data = policy_cache.get(epd)
            if not policy_data or not policy_data.get("policy"):
                continue
            
            policy = policy_data["policy"]
            top_k = metrics.DEFAULT_CONFIG.steer_top_k
            top_moves = policy[:top_k]
            
            candidates = []
            
            for p_entry in top_moves:
                uci = p_entry.get("uci")
                try:
                    move = board_before.parse_uci(uci)
                except ValueError:
                    continue
                    
                board_after = board_before.copy(stack=False)
                board_after.push(move)
                fen_after_m = board_after.fen()
                epd_after_m = board_after.epd()
                
                s_data = steer_cache.get(epd_after_m)
                if not s_data:
                    analysis = await engine.analyze(
                        fen_after_m, depth=None, multipv=2,
                        time_limit=metrics.DEFAULT_CONFIG.confirm_played_seconds)
                    if not analysis:
                        raise Exception("engine in mock mode")
                    pol_after = await engine.get_policy_distribution(fen_after_m, nodes=1)
                    s_data = {"analysis": analysis, "policy": pol_after}
                    steer_cache.put(epd_after_m, s_data)
                    
                analysis_after = s_data["analysis"]
                policy_after = s_data["policy"]
                
                if bt3_budget_remaining > 0:
                    saliency = vision.saliency_absolute(fen_after_m)
                    bt3_budget_remaining -= 1
                else:
                    saliency = None
                    
                complexity = metrics.tactical_complexity(analysis_after, policy_after, saliency)
                
                cp_eval = metrics.eval_cp_number(analysis_after.get("evaluation"))
                if cp_eval is None:
                    continue
                # evaluation is white-POV after move. If mover is white, they want it positive (white winning).
                # If mover is black, they want it negative (black winning).
                eval_cp_mover = cp_eval if user_color == chess.WHITE else -cp_eval
                
                candidates.append({
                    "uci": uci,
                    "san": p_entry.get("san"),
                    "eval_cp": eval_cp_mover,
                    "complexity": complexity["score"],
                    "components": complexity
                })
                
            if not candidates:
                continue
                
            best_eval_cp = max(c["eval_cp"] for c in candidates)
            steer_res = metrics.steer_candidates(candidates, best_eval_cp)
            
            if steer_res["had_tal_move"] or (steer_res["objective_best"] and steer_res["objective_best"]["complexity"] >= 0.6):
                opening_match = openings.classify(node["uci_moves_so_far"])
                eco = opening_match["eco"] if opening_match else "???"
                
                best_c = steer_res["objective_best"]
                tal_c = steer_res["tal_move"]
                
                steer_findings.append({
                    "id": f"s-{node['game_idx']:03d}-p{node['ply']:03d}",
                    "game": {
                        "white": node["game"].headers.get("White", "?"),
                        "black": node["game"].headers.get("Black", "?"),
                        "date": node["game"].headers.get("Date", "?")
                    },
                    "ply": node["ply"],
                    "fen_before": fen_before,
                    "best": {"uci": best_c["uci"], "san": best_c["san"], "eval_cp": best_c["eval_cp"], "complexity": best_c["complexity"], "components": best_c["components"]},
                    "steer": {"uci": tal_c["uci"], "san": tal_c["san"], "eval_cp": tal_c["eval_cp"], "complexity": tal_c["complexity"], "components": tal_c["components"]} if tal_c else {"uci": best_c["uci"], "san": best_c["san"], "eval_cp": best_c["eval_cp"], "complexity": best_c["complexity"], "components": best_c["components"]},
                    "playable_candidates": [{"uci": c["uci"], "complexity": c["complexity"], "eval_cp": c["eval_cp"]} for c in steer_res["playable"]],
                    "eval_loss_cp": best_eval_cp - (tal_c["eval_cp"] if tal_c else best_eval_cp),
                    "had_tal_move": steer_res["had_tal_move"],
                    "opening": {"eco": eco}
                })
                
                by_opening_steer[eco]["tal_moves"] += 1 if steer_res["had_tal_move"] else 0
                
            # Keep aggregate for ALL nodes processed
            opening_match_all = openings.classify(node["uci_moves_so_far"])
            eco_all = opening_match_all["eco"] if opening_match_all else "???"
            by_opening_steer[eco_all]["moves"] += 1
            if candidates and steer_res["objective_best"]:
                by_opening_steer[eco_all]["complexity_sum"] += steer_res["objective_best"]["complexity"]

            steer_processed += 1
            if steer_processed % 10 == 0:
                _progress(job_id, stage_steer_done=steer_processed)

        steer_summary = {}
        for eco, st in by_opening_steer.items():
            steer_summary[eco] = {
                "moves": st["moves"],
                "tal_moves": st["tal_moves"],
                "mean_complexity": st["complexity_sum"] / max(1, st["moves"])
            }
            
        # Aggregate
        by_motif = defaultdict(lambda: {"missed": 0, "blind": 0, "confirmed": 0})
        by_opening = defaultdict(lambda: {"moves": 0, "missed": 0, "blind": 0, "blind_rate": 0.0})
        by_concept = defaultdict(lambda: {"missed": 0})
        
        intuitive_blind_count = 0
        attention_blind_count = 0
        
        for game_idx, (game, user_color) in enumerate(games_to_process):
            board = game.board()
            uci_moves = []
            for node in game.mainline():
                uci_moves.append(node.move.uci())
                if board.turn == user_color and not is_time_scramble(node.comment):
                    opening_match = openings.classify(uci_moves)
                    if opening_match:
                        by_opening[opening_match["eco"]]["moves"] += 1
                board.push(node.move)
                
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
            "time_scramble_skipped": scramble_skipped,
            "findings": findings,
            "aggregates": aggregates,
            "steer_findings": steer_findings,
            "steer_summary": steer_summary
        }
        
        from backend.training import attempts
        profile["regressions"] = attempts.escalate_regressions(profile)

        store.save_profile(profile)
        store.update_job(job_id, status="done")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        store.update_job(job_id, status="error", error=str(e))
