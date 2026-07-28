"""
Relational-Fact Extractor — pure, deterministic decoding of position and line semantics.

Translates positions and tactical forcing lines into grounded piece-relationship facts:
- Protected passed pawns
- Attacks on valuable enemy pieces (Q/R)
- Absolute and relative pins / x-rays (hardened with python-chess board.pin)
- Conditional pins (recapture / hypothetical placement pins)
- Defender removal (squares controlled by captured pieces)
- King pressure assessment
- Positional pawn weaknesses (isolated, doubled, backward)
- Tied defenders (pieces tied to defending weak, attacked pawns)
- Outposts (enemy pieces occupying unchallenged holes in friendly territory)
"""

from typing import List, Dict, Any, Optional, Union
import chess
from backend.lichess_tagger import util


def _sign(x: int) -> int:
    return 1 if x > 0 else (-1 if x < 0 else 0)


def _is_slider_ray(sq1: int, sq2: int, piece_type: chess.PieceType) -> bool:
    r1, f1 = chess.square_rank(sq1), chess.square_file(sq1)
    r2, f2 = chess.square_rank(sq2), chess.square_file(sq2)
    if piece_type in (chess.ROOK, chess.QUEEN):
        if r1 == r2 or f1 == f2:
            return True
    if piece_type in (chess.BISHOP, chess.QUEEN):
        if (r1 - f1 == r2 - f2) or (r1 + f1 == r2 + f2):
            return True
    return False


def _ray_directions(piece_type: chess.PieceType) -> List[tuple[int, int]]:
    dirs = []
    if piece_type in (chess.ROOK, chess.QUEEN):
        dirs.extend([(1, 0), (-1, 0), (0, 1), (0, -1)])
    if piece_type in (chess.BISHOP, chess.QUEEN):
        dirs.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])
    return dirs


def protected_passed_pawns(board: chess.Board, pov: chess.Color) -> List[Dict[str, Any]]:
    """
    Find pawns of color `pov` with no enemy pawn able to stop them (same or adjacent file ahead),
    defended by at least one friendly piece.
    """
    facts = []
    pawns = board.pieces(chess.PAWN, pov)

    for pawn_sq in pawns:
        f = chess.square_file(pawn_sq)
        r = chess.square_rank(pawn_sq)

        is_passed = True
        if pov == chess.WHITE:
            ranks_ahead = range(r + 1, 8)
            distance = 7 - r
        else:
            ranks_ahead = range(0, r)
            distance = r

        files_to_check = [file_idx for file_idx in (f - 1, f, f + 1) if 0 <= file_idx <= 7]

        for check_rank in ranks_ahead:
            for check_file in files_to_check:
                sq = chess.square(check_file, check_rank)
                p = board.piece_at(sq)
                if p and p.piece_type == chess.PAWN and p.color != pov:
                    is_passed = False
                    break
            if not is_passed:
                break

        if is_passed:
            defenders_bb = board.attackers(pov, pawn_sq)
            if defenders_bb:
                defenders = [chess.square_name(d) for d in defenders_bb]
                pawn_name = chess.square_name(pawn_sq)
                def_str = ", ".join(defenders)
                dist_str = f"{distance} square{'s' if distance > 1 else ''}"
                facts.append({
                    "kind": "protected_passed_pawn",
                    "square": pawn_name,
                    "pawn": pawn_name,
                    "distance": distance,
                    "defenders": defenders,
                    "text": f"Protected passed pawn on {pawn_name} defended by {def_str}, {dist_str} from queening",
                })

    return facts


def attacks_on_valuable(board: chess.Board, pov: chess.Color) -> List[Dict[str, Any]]:
    """
    Find pov pieces or pawns attacking an enemy Queen or Rook (valuable pieces >= 5).
    """
    facts = []
    enemy_color = not pov

    for enemy_sq, enemy_piece in board.piece_map().items():
        if enemy_piece.color == enemy_color and enemy_piece.piece_type in (chess.QUEEN, chess.ROOK):
            attackers = board.attackers(pov, enemy_sq)
            for attacker_sq in attackers:
                attacker_piece = board.piece_at(attacker_sq)
                if attacker_piece:
                    att_str = attacker_piece.symbol().upper()
                    att_sq_name = chess.square_name(attacker_sq)
                    tgt_str = enemy_piece.symbol().upper()
                    tgt_sq_name = chess.square_name(enemy_sq)
                    facts.append({
                        "kind": "attack_on_valuable",
                        "attacker_square": att_sq_name,
                        "attacker_piece": att_str,
                        "target_square": tgt_sq_name,
                        "target_piece": tgt_str,
                        "text": f"{att_str} on {att_sq_name} attacks {tgt_str} on {tgt_sq_name}",
                    })

    return facts


def pins_and_xrays(board: chess.Board, pov: chess.Color) -> List[Dict[str, Any]]:
    """
    Find genuine absolute and relative pins/x-rays of enemy pieces by pov sliders.
    Uses board.pin for absolute pins to King and strict ray-walking for relative pins.
    """
    facts = []
    enemy_color = not pov
    seen_pins = set()

    # 1. Absolute pins to King using python-chess board.pin
    king_sq = board.king(enemy_color)
    if king_sq is not None:
        for enemy_sq, enemy_piece in board.piece_map().items():
            if enemy_piece.color == enemy_color and enemy_piece.piece_type != chess.KING:
                pin_dir = board.pin(enemy_color, enemy_sq)
                if pin_dir != chess.BB_ALL:
                    # Find friendly slider on pin ray
                    for attacker_sq in pin_dir:
                        attacker = board.piece_at(attacker_sq)
                        if attacker and attacker.color == pov and attacker.piece_type in (chess.BISHOP, chess.ROOK, chess.QUEEN):
                            if attacker_sq in board.attackers(pov, enemy_sq):
                                att_sq_name = chess.square_name(attacker_sq)
                                pin_sq_name = chess.square_name(enemy_sq)
                                king_sq_name = chess.square_name(king_sq)
                                p_str = enemy_piece.symbol().upper()
                                key = (att_sq_name, pin_sq_name, king_sq_name)
                                if key not in seen_pins:
                                    seen_pins.add(key)
                                    facts.append({
                                        "kind": "pin_or_xray",
                                        "attacker_square": att_sq_name,
                                        "pinned_square": pin_sq_name,
                                        "target_square": king_sq_name,
                                        "pinned_to": "K",
                                        "text": f"{p_str} on {pin_sq_name} is pinned by {att_sq_name} to K on {king_sq_name}",
                                    })

    # 2. Relative pins / x-rays to more valuable enemy pieces
    for attacker_sq, attacker in board.piece_map().items():
        if attacker.color == pov and attacker.piece_type in (chess.BISHOP, chess.ROOK, chess.QUEEN):
            for dr, df in _ray_directions(attacker.piece_type):
                r, f = chess.square_rank(attacker_sq) + dr, chess.square_file(attacker_sq) + df
                pieces_on_ray = []

                while 0 <= r <= 7 and 0 <= f <= 7:
                    sq = chess.square(f, r)
                    p = board.piece_at(sq)
                    if p is not None:
                        pieces_on_ray.append((sq, p))
                        if len(pieces_on_ray) == 2:
                            break
                    r += dr
                    f += df

                if len(pieces_on_ray) == 2:
                    (p1_sq, p1), (p2_sq, p2) = pieces_on_ray
                    if p1.color == enemy_color and p2.color == enemy_color:
                        val1 = util.values.get(p1.piece_type, 0)
                        val2 = util.values.get(p2.piece_type, 99 if p2.piece_type == chess.KING else 0)
                        if val2 > val1 or p2.piece_type == chess.KING:
                            att_sq_name = chess.square_name(attacker_sq)
                            p1_sq_name = chess.square_name(p1_sq)
                            p2_sq_name = chess.square_name(p2_sq)
                            key = (att_sq_name, p1_sq_name, p2_sq_name)
                            if key not in seen_pins:
                                seen_pins.add(key)
                                p1_str = p1.symbol().upper()
                                p2_str = "K" if p2.piece_type == chess.KING else p2.symbol().upper()
                                facts.append({
                                    "kind": "pin_or_xray",
                                    "attacker_square": att_sq_name,
                                    "pinned_square": p1_sq_name,
                                    "target_square": p2_sq_name,
                                    "pinned_to": p2_str,
                                    "text": f"{p1_str} on {p1_sq_name} is pinned by {att_sq_name} to {p2_str} on {p2_sq_name}",
                                })

    return facts


def conditional_pins(board: chess.Board, pov: chess.Color, square: Union[int, str]) -> List[Dict[str, Any]]:
    """
    Check if placing a hypothetical enemy piece on `square` would pin it by a pov slider
    to a more valuable enemy piece (Q/R/K).
    """
    facts = []
    if isinstance(square, str):
        target_sq = chess.parse_square(square)
    else:
        target_sq = square

    enemy_color = not pov
    test_board = board.copy()

    # Place hypothetical enemy knight on target_sq
    hypothetical_piece = chess.Piece(chess.KNIGHT, enemy_color)
    test_board.set_piece_at(target_sq, hypothetical_piece)

    for attacker_sq, attacker in test_board.piece_map().items():
        if attacker.color == pov and attacker.piece_type in (chess.BISHOP, chess.ROOK, chess.QUEEN):
            if _is_slider_ray(attacker_sq, target_sq, attacker.piece_type):
                # Check ray between attacker_sq and target_sq is clear
                between_1 = chess.SquareSet.between(attacker_sq, target_sq)
                if all(test_board.piece_at(s) is None for s in between_1):
                    # Continue ray past target_sq
                    dr = _sign(chess.square_rank(target_sq) - chess.square_rank(attacker_sq))
                    df = _sign(chess.square_file(target_sq) - chess.square_file(attacker_sq))

                    r = chess.square_rank(target_sq) + dr
                    f = chess.square_file(target_sq) + df

                    behind_piece_sq = None
                    behind_piece = None

                    while 0 <= r <= 7 and 0 <= f <= 7:
                        sq = chess.square(f, r)
                        p = test_board.piece_at(sq)
                        if p is not None:
                            behind_piece_sq = sq
                            behind_piece = p
                            break
                        r += dr
                        f += df

                    if behind_piece and behind_piece.color == enemy_color:
                        if behind_piece.piece_type in (chess.QUEEN, chess.KING, chess.ROOK) or util.values.get(behind_piece.piece_type, 0) > util.values[chess.KNIGHT]:
                            sq_name = chess.square_name(target_sq)
                            att_name = chess.square_name(attacker_sq)
                            behind_name = chess.square_name(behind_piece_sq)
                            tgt_str = "K" if behind_piece.piece_type == chess.KING else behind_piece.symbol().upper()
                            enemy_color_name = chess.COLOR_NAMES[enemy_color].capitalize()
                            facts.append({
                                "kind": "conditional_pin",
                                "square": sq_name,
                                "attacker_square": att_name,
                                "target_square": behind_name,
                                "target_piece": tgt_str,
                                "text": f"A {enemy_color_name} piece on {sq_name} would be pinned by {att_name} to {tgt_str} on {behind_name}",
                            })

    return facts


def defender_removed(board_before: chess.Board, move: Union[chess.Move, str], pov: chess.Color) -> Optional[Dict[str, Any]]:
    """
    If move is a capture of an enemy piece, return a fact stating which squares were controlled by the captured piece.
    """
    if isinstance(move, str):
        move_obj = chess.Move.from_uci(move)
    else:
        move_obj = move

    if not board_before.is_capture(move_obj):
        return None

    to_sq = move_obj.to_square
    if board_before.is_en_passant(move_obj):
        captured_sq = chess.square(chess.square_file(to_sq), chess.square_rank(move_obj.from_square))
    else:
        captured_sq = to_sq

    captured_piece = board_before.piece_at(captured_sq)
    if not captured_piece or captured_piece.color == pov:
        return None

    controlled_sqs = list(board_before.attacks(captured_sq))
    controlled_names = [chess.square_name(s) for s in controlled_sqs]
    cap_str = captured_piece.symbol().upper()
    cap_sq_name = chess.square_name(captured_sq)
    ctrl_str = ", ".join(controlled_names)

    return {
        "kind": "defender_removed",
        "captured_piece": cap_str,
        "captured_square": cap_sq_name,
        "controlled_squares": controlled_names,
        "text": f"Capturing {cap_str} on {cap_sq_name} removes defender of {ctrl_str}",
    }


def king_pressure(board: chess.Board, pov: chess.Color) -> List[Dict[str, Any]]:
    """
    Assess enemy king safety: shield pawn count, adjacent defenders count, king square.
    """
    facts = []
    enemy_color = not pov
    enemy_king_sq = board.king(enemy_color)

    if enemy_king_sq is None:
        return facts

    k_rank = chess.square_rank(enemy_king_sq)
    k_file = chess.square_file(enemy_king_sq)

    # Shield pawns (1-2 ranks ahead of enemy king within 1 file)
    shield_pawn_count = 0
    rank_dir = 1 if enemy_color == chess.WHITE else -1
    shield_ranks = [k_rank + rank_dir, k_rank + 2 * rank_dir]
    shield_files = [f for f in (k_file - 1, k_file, k_file + 1) if 0 <= f <= 7]

    for r in shield_ranks:
        if 0 <= r <= 7:
            for f in shield_files:
                p = board.piece_at(chess.square(f, r))
                if p and p.piece_type == chess.PAWN and p.color == enemy_color:
                    shield_pawn_count += 1

    # Adjacent defenders (non-pawn, non-king enemy pieces adjacent to enemy king)
    defender_count = 0
    for s, p in board.piece_map().items():
        if p.color == enemy_color and p.piece_type not in (chess.PAWN, chess.KING):
            if chess.square_distance(s, enemy_king_sq) == 1:
                defender_count += 1

    k_name = chess.square_name(enemy_king_sq)
    facts.append({
        "kind": "king_pressure",
        "king_square": k_name,
        "shield_pawns": shield_pawn_count,
        "adjacent_defenders": defender_count,
        "text": f"Enemy king on {k_name} has {shield_pawn_count} shield pawn(s) and {defender_count} adjacent defender(s)",
    })

    return facts


def pawn_weaknesses(board: chess.Board, color: chess.Color) -> List[Dict[str, Any]]:
    """
    Detect pawn weaknesses for `color`: isolated, doubled, and backward pawns.
    """
    facts = []
    dr = 1 if color == chess.WHITE else -1
    pawns = list(board.pieces(chess.PAWN, color))
    pawns_by_file: Dict[int, List[int]] = {}

    for sq in pawns:
        f = chess.square_file(sq)
        pawns_by_file.setdefault(f, []).append(sq)

    # 1. Doubled pawns (reported once per file)
    for f, sqs in sorted(pawns_by_file.items()):
        if len(sqs) > 1:
            file_name = chr(ord('a') + f)
            sq_names = [chess.square_name(s) for s in sorted(sqs)]
            any_attacked = any(bool(board.attackers(not color, s)) for s in sqs)
            color_name = chess.COLOR_NAMES[color].capitalize()
            att_str = " (and under attack)" if any_attacked else ""
            facts.append({
                "kind": "pawn_weakness",
                "weakness": "doubled",
                "file": file_name,
                "squares": sq_names,
                "square": sq_names[0],
                "color": color_name,
                "attacked": any_attacked,
                "text": f"{color_name}'s pawns on file {file_name} ({', '.join(sq_names)}) are doubled{att_str}",
            })

    for sq in sorted(pawns):
        f = chess.square_file(sq)
        r = chess.square_rank(sq)
        sq_name = chess.square_name(sq)
        color_name = chess.COLOR_NAMES[color].capitalize()
        is_attacked = bool(board.attackers(not color, sq))
        att_str = " (and under attack)" if is_attacked else ""

        # 2. Isolated pawn check
        adj_files = [f_adj for f_adj in (f - 1, f + 1) if 0 <= f_adj <= 7]
        has_adj_pawn = any(f_adj in pawns_by_file for f_adj in adj_files)
        if not has_adj_pawn:
            facts.append({
                "kind": "pawn_weakness",
                "weakness": "isolated",
                "square": sq_name,
                "color": color_name,
                "attacked": is_attacked,
                "text": f"{color_name}'s {sq_name} pawn is isolated{att_str}",
            })

        # 3. Backward pawn check
        adj_support = False
        for f_adj in adj_files:
            for s_adj in pawns_by_file.get(f_adj, []):
                r_adj = chess.square_rank(s_adj)
                if r_adj * dr <= r * dr:
                    adj_support = True
                    break
            if adj_support:
                break

        if not adj_support:
            stop_r = r + dr
            if 0 <= stop_r <= 7:
                stop_sq = chess.square(f, stop_r)
                stop_piece = board.piece_at(stop_sq)
                stop_occ_by_enemy_pawn = (
                    stop_piece is not None
                    and stop_piece.piece_type == chess.PAWN
                    and stop_piece.color != color
                )
                stop_ctrl_by_enemy_pawn = any(
                    board.piece_at(att_sq).piece_type == chess.PAWN
                    for att_sq in board.attackers(not color, stop_sq)
                    if board.piece_at(att_sq) and board.piece_at(att_sq).color != color
                )

                if stop_occ_by_enemy_pawn or stop_ctrl_by_enemy_pawn:
                    friendly_pawn_ahead = any(
                        chess.square_rank(s_f) * dr > r * dr
                        for s_f in pawns_by_file.get(f, [])
                    )
                    if not friendly_pawn_ahead:
                        facts.append({
                            "kind": "pawn_weakness",
                            "weakness": "backward",
                            "square": sq_name,
                            "color": color_name,
                            "attacked": is_attacked,
                            "text": f"{color_name}'s {sq_name} pawn is backward{att_str}",
                        })

    return facts


def tied_defenders(board: chess.Board, color: chess.Color) -> List[Dict[str, Any]]:
    """
    Find color pieces tied to defending a weak friendly pawn currently under attack.
    """
    facts = []
    weaknesses = pawn_weaknesses(board, color)
    weak_pawns = set()

    for w in weaknesses:
        if w["weakness"] in ("isolated", "backward"):
            weak_pawns.add(chess.parse_square(w["square"]))
        elif w["weakness"] == "doubled":
            for sq_name in w.get("squares", []):
                weak_pawns.add(chess.parse_square(sq_name))

    seen = set()

    for w_sq in sorted(weak_pawns):
        enemy_attackers = board.attackers(not color, w_sq)
        if enemy_attackers:
            friendly_attackers = board.attackers(color, w_sq)
            for def_sq in sorted(friendly_attackers):
                def_piece = board.piece_at(def_sq)
                if def_piece and def_piece.piece_type not in (chess.PAWN, chess.KING):
                    key = (def_sq, w_sq)
                    if key not in seen:
                        seen.add(key)
                        def_sq_name = chess.square_name(def_sq)
                        w_sq_name = chess.square_name(w_sq)
                        p_str = def_piece.symbol().upper()
                        facts.append({
                            "kind": "tied_defender",
                            "piece": p_str,
                            "square": def_sq_name,
                            "defends": w_sq_name,
                            "text": f"The {p_str} on {def_sq_name} is tied to the defence of the weak {w_sq_name} pawn",
                        })

    return facts


def outposts(board: chess.Board, color: chess.Color) -> List[Dict[str, Any]]:
    """
    Detect enemy pieces (knight, bishop, rook) sitting on outposts in color's half of the board.
    """
    facts = []
    enemy_color = not color
    dr = 1 if color == chess.WHITE else -1
    half_ranks = range(0, 4) if color == chess.WHITE else range(4, 8)

    for sq, piece in sorted(board.piece_map().items()):
        if piece.color == enemy_color and piece.piece_type in (chess.KNIGHT, chess.BISHOP, chess.ROOK):
            r = chess.square_rank(sq)
            if r in half_ranks:
                f = chess.square_file(sq)
                adj_files = [f_adj for f_adj in (f - 1, f + 1) if 0 <= f_adj <= 7]

                can_be_challenged = False
                color_pawns = board.pieces(chess.PAWN, color)

                for p_sq in color_pawns:
                    p_f = chess.square_file(p_sq)
                    p_r = chess.square_rank(p_sq)
                    if p_f in adj_files:
                        if p_r * dr < r * dr:
                            can_be_challenged = True
                            break

                if not can_be_challenged:
                    sq_name = chess.square_name(sq)
                    p_str = piece.symbol().upper()
                    color_name = chess.COLOR_NAMES[color].capitalize()
                    facts.append({
                        "kind": "outpost",
                        "enemy_piece": p_str,
                        "square": sq_name,
                        "defender_color": color_name,
                        "text": f"The enemy {p_str} on {sq_name} sits on an outpost — a hole {color_name} can no longer challenge with a pawn",
                    })

    return facts


def relational_facts(fen: str, line_ucis: List[str], pov: chess.Color) -> Dict[str, Any]:
    """
    Composition API: applies relational fact extractors to initial position and along line_ucis,
    recording what each move creates and removes.
    """
    board = chess.Board(fen)

    position_facts = []
    position_facts.extend(protected_passed_pawns(board, pov))
    position_facts.extend(attacks_on_valuable(board, pov))
    position_facts.extend(pins_and_xrays(board, pov))
    position_facts.extend(king_pressure(board, pov))
    position_facts.extend(pawn_weaknesses(board, pov))
    position_facts.extend(tied_defenders(board, pov))
    position_facts.extend(outposts(board, pov))

    per_move = []

    for move_uci in line_ucis:
        move_obj = chess.Move.from_uci(move_uci)
        board_before = board.copy()

        def_rem = defender_removed(board_before, move_obj, pov)
        cond_pins = conditional_pins(board_before, pov, move_obj.to_square)

        board.push(move_obj)
        board_after = board.copy()

        facts_before = (
            protected_passed_pawns(board_before, pov)
            + attacks_on_valuable(board_before, pov)
            + pins_and_xrays(board_before, pov)
            + pawn_weaknesses(board_before, pov)
            + tied_defenders(board_before, pov)
            + outposts(board_before, pov)
        )
        facts_after = (
            protected_passed_pawns(board_after, pov)
            + attacks_on_valuable(board_after, pov)
            + pins_and_xrays(board_after, pov)
            + pawn_weaknesses(board_after, pov)
            + tied_defenders(board_after, pov)
            + outposts(board_after, pov)
        )

        before_texts = {f["text"] for f in facts_before}
        after_texts = {f["text"] for f in facts_after}

        creates = [f for f in facts_after if f["text"] not in before_texts]
        for cp in cond_pins:
            if cp["text"] not in {f["text"] for f in creates}:
                creates.append(cp)

        removes = []
        if def_rem:
            removes.append(def_rem)

        removed_pos = [f for f in facts_before if f["text"] not in after_texts]
        for r_fact in removed_pos:
            if r_fact["text"] not in {f["text"] for f in removes}:
                removes.append(r_fact)

        per_move.append({
            "move": move_uci,
            "creates": creates,
            "removes": removes,
        })

    return {
        "position_facts": position_facts,
        "per_move": per_move,
    }
