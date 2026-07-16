"""
Neural Vision implementation.
Fallback mode: 'policy_fallback'
(Genuine lczerolens extraction is blocked by Windows Store Python 3.9 / Torch compatibility).
"""
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class NeuralVision:
    def __init__(self, weights_path: str):
        self.weights_path = weights_path
        logger.warning("Initializing NeuralVision in fallback mode due to lczerolens blocker.")

    def is_available(self) -> bool:
        # Fallback is always available
        return True

    def saliency(self, fen: str, policy_dist: list[dict] = None) -> dict[str, float]:
        """
        Derive a saliency proxy by aggregating Phase-1 policy priors onto squares.
        Returns {square_name: score in [0,1]} for all 64 squares.
        """
        saliency_map = {f"{f}{r}": 0.0 for f in "abcdefgh" for r in "12345678"}
        
        if not policy_dist:
            return saliency_map
            
        # Sum each move's p onto its from and to squares
        for move in policy_dist:
            p = move.get("p", 0.0)
            frm = move.get("from")
            to = move.get("to")
            
            if frm in saliency_map:
                saliency_map[frm] += p
            if to in saliency_map:
                saliency_map[to] += p
                
        # Normalize to [0,1]
        max_val = max(saliency_map.values()) if saliency_map else 0.0
                
        if max_val > 0:
            for sq in saliency_map:
                saliency_map[sq] /= max_val
                
        return saliency_map
