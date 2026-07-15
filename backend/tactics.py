import chess
import chess.pgn
from typing import List, Set
from backend.lichess_tagger import Puzzle, cook

class MotifDetector:
    @classmethod
    def analyze_pv(cls, starting_fen: str, pv_san: List[str]) -> Set[str]:
        """
        Uses the official Lichess Python Tagger to detect tactical motifs in a PV.
        """
        if not pv_san:
            return set()
            
        try:
            # 1. Create a chess.pgn.Game from the starting position
            board = chess.Board(starting_fen)
            game = chess.pgn.Game()
            game.setup(board)
            
            # 2. Add the PV moves to build the mainline
            node = game
            for san in pv_san:
                # We need to make sure the move is legal and valid
                move = board.parse_san(san)
                node = node.add_variation(move)
                board.push(move)
                
            # 3. Create the Puzzle object. 
            # Note: Lichess requires a 'cp' (centipawn score), but for motif detection (cook.py),
            # it mostly relies on the board state geometry rather than the exact score.
            # We can pass a dummy winning score (e.g., 500) since we know the PV is forcing.
            puzzle = Puzzle(id="lc0_pv", game=game, cp=500)
            
            # 4. Cook the puzzle to get tags
            tags = cook(puzzle)
            
            # Return as a set of unique motifs
            return set(tags)
            
        except Exception as e:
            # If there's an issue with the PV (illegal moves, etc.), fail gracefully
            print(f"Error in Lichess tagger: {e}")
            return set()
