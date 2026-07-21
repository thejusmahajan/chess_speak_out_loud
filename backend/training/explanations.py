import chess
from backend.training import store
from backend import llm_client

async def enrich_tree_explanations(tree: dict, max_new: int = 8, model: str = "gemini-3.5-flash") -> dict:
    """
    Attaches coach explanations to critical nodes in the repertoire variation tree.
    Uses store.EpdCache("explanations") for caching and bounds new generations
    per request via max_new.
    """
    if not isinstance(tree, dict) or "nodes" not in tree:
        return tree

    cache = store.EpdCache("explanations")
    new_count = 0

    nodes = tree.get("nodes", [])
    if not isinstance(nodes, list):
        return tree

    for node in nodes:
        if not isinstance(node, dict):
            continue

        # Only process critical user nodes
        if not node.get("critical"):
            continue

        user_move = node.get("user_move")
        if not isinstance(user_move, dict) or not user_move.get("uci"):
            continue

        fen_before = node.get("fen_before")
        if not fen_before or not isinstance(fen_before, str):
            continue

        try:
            epd = chess.Board(fen_before).epd()
        except Exception:
            # Skip malformed positions gracefully
            continue

        cached = cache.get(epd)
        if cached and isinstance(cached, dict) and cached.get("explanation"):
            node["explanation"] = cached["explanation"]
        else:
            if new_count < max_new:
                opening_name = tree.get("opening_name") or tree.get("eco", "Unknown Opening")
                color = tree.get("color", "white")

                context = {
                    "fen": fen_before,
                    "move_san": user_move.get("san", ""),
                    "move_uci": user_move.get("uci", ""),
                    "critical_reason": node.get("critical_reason", ""),
                    "eval_cp": node.get("eval_cp", 0),
                    "user_blind_rate": node.get("user_blind_rate", 0.0),
                    "opponent_replies": node.get("opponent_replies", []),
                    "color": color,
                    "opening_name": opening_name,
                }

                explanation_text = await llm_client.generate_move_explanation(context, model)
                cache.put(epd, {
                    "explanation": explanation_text,
                    "move_uci": user_move.get("uci")
                })
                node["explanation"] = explanation_text
                new_count += 1

    return tree
