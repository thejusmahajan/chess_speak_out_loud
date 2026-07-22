"""
Neural Vision implementation.
Retrieves real transformer encoder attention saliency from lczerolens via ONNX.
"""
import logging
import os
import tempfile
from pathlib import Path
import chess

logger = logging.getLogger(__name__)

class NeuralVision:
    def __init__(self, onnx_path: str):
        self.mode = "policy_fallback"
        self.model = None
        self._attn_module_names = [
            f"module.encoder{i}/mha/QK/softmax" for i in range(15)
        ]
        
        try:
            import torch
            import lczerolens
            from lczerolens import LczeroModel

            # Monkey patch for Windows NamedTemporaryFile issue inside onnx2torch
            import lczerolens.model
            original_safe = lczerolens.model.safe_shape_inference
            def patched_safe_shape_inference(onnx_model_or_path, **kwargs):
                if not isinstance(onnx_model_or_path, (str, os.PathLike)):
                    return original_safe(onnx_model_or_path, **kwargs)
                fd, path = tempfile.mkstemp(dir=Path(onnx_model_or_path).parent)
                os.close(fd)
                try:
                    import onnx2torch.utils.safe_shape_inference as ssi
                    res = ssi._shape_inference_by_model_path(onnx_model_or_path, output_path=path, **kwargs)
                    return res
                finally:
                    try: os.remove(path)
                    except OSError: pass
            lczerolens.model.safe_shape_inference = patched_safe_shape_inference

            self.model = LczeroModel.from_onnx_path(onnx_path)
            self.model.eval()
            self.mode = "attention"
            logger.info("NeuralVision loaded BT3 ONNX in attention mode.")
        except Exception as exc:
            logger.warning("NeuralVision attention unavailable (%s) — policy_fallback", exc)

    def is_available(self) -> bool:
        return True
        
    def saliency(self, fen: str, policy_dist: list[dict] = None) -> dict[str, float]:
        if self.mode == "attention" and self.model is not None:
            try:
                return self._attention_saliency(fen)
            except Exception as exc:
                logger.error("attention saliency failed (%s) — fallback", exc)
        return self._policy_fallback(fen, policy_dist)

    def _attention_saliency(self, fen: str) -> dict[str, float]:
        import torch
        from lczerolens import LczeroBoard
        
        attention_tensors = []
        
        def hook_fn(module, inp, out):
            t = out[0] if isinstance(out, (tuple, list)) else out
            attention_tensors.append(t.detach())
            
        hooks = []
        for name, mod in self.model.named_modules():
            if name in self._attn_module_names:
                hooks.append(mod.register_forward_hook(hook_fn))
                
        board = LczeroBoard(fen)
        with torch.no_grad():
            self.model(board)
            
        for h in hooks:
            h.remove()
            
        if not attention_tensors:
            raise RuntimeError("No attention tensors captured")
            
        # attention_tensors has tensors of shape [batch, heads, 64, 64]
        stacked = torch.stack(attention_tensors)
        
        # Average over layers (0) and heads (2) and batch (1)
        # shape [15, 1, 24, 64, 64] -> mean(0,1,2) -> [64, 64]
        avg_attn = stacked.mean(dim=(0, 1, 2))
        
        # We want the attention *received* per square (source),
        # so we average over the queries (axis=0).
        saliency_vec = avg_attn.mean(dim=0)
        
        # Normalize to [0,1]
        max_val = saliency_vec.max()
        min_val = saliency_vec.min()
        if max_val > min_val:
            saliency_vec = (saliency_vec - min_val) / (max_val - min_val)
        else:
            saliency_vec = torch.zeros_like(saliency_vec)
            
        saliency_vec = saliency_vec.tolist()
        
        saliency_map = {}
        files = "abcdefgh"
        ranks = "12345678"
        
        # LC0 token 0 is a1 from White's view
        for i in range(64):
            rank_idx = i // 8
            file_idx = i % 8
            sq = f"{files[file_idx]}{ranks[rank_idx]}"
            saliency_map[sq] = saliency_vec[i]
            
        return saliency_map

    def saliency_absolute(self, fen: str) -> dict[str, float]:
        """
        Public API: BT3 attention saliency keyed by TRUE absolute squares,
        correct for BOTH white-to-move and black-to-move positions.

        Training-system code (diagnostician, drills, hidden gems) MUST use
        this instead of saliency(), which is only frame-correct for
        white-to-move positions. Falls back to policy_fallback shape (all
        zeros without a policy dist) if attention mode is unavailable.
        """
        if self.mode != "attention" or self.model is None:
            return self._policy_fallback(fen, None)
        try:
            return self._saliency_absolute(chess.Board(fen))
        except Exception as exc:
            logger.error("saliency_absolute failed (%s) — fallback", exc)
            return self._policy_fallback(fen, None)

    def saliency_absolute_batch(self, fens: list[str]) -> list[dict[str, float]]:
        """
        Public API: Batched BT3 attention saliency for a list of FENs, keyed by
        TRUE absolute squares, correct for BOTH white- and black-to-move positions.
        Runs ONE forward pass for the whole list.

        Falls back to policy_fallback per FEN if attention mode is unavailable, or
        to serial _saliency_absolute on any error in the batched path.
        """
        if not fens:
            return []
        if self.mode != "attention" or self.model is None:
            return [self._policy_fallback(f, None) for f in fens]
        try:
            return self._saliency_absolute_batch(fens)
        except Exception as exc:
            logger.error("saliency_absolute_batch failed (%s) — fallback to serial", exc)
            return [self._saliency_absolute(chess.Board(f)) for f in fens]

    def _saliency_absolute_batch(self, fens: list[str]) -> list[dict[str, float]]:
        import torch
        from lczerolens import LczeroBoard

        boards = [chess.Board(f) for f in fens]
        input_tensors = []
        is_black_list = []

        for b in boards:
            is_black = (b.turn == chess.BLACK)
            is_black_list.append(is_black)
            eval_fen = b.mirror().fen() if is_black else b.fen()
            input_tensors.append(LczeroBoard(eval_fen).to_input_tensor())

        batch_tensor = torch.stack(input_tensors)

        attention_tensors = []
        def hook_fn(module, inp, out):
            t = out[0] if isinstance(out, (tuple, list)) else out
            attention_tensors.append(t.detach())

        hooks = [
            mod.register_forward_hook(hook_fn)
            for name, mod in self.model.named_modules()
            if name in self._attn_module_names
        ]

        try:
            with torch.no_grad():
                self.model(batch_tensor)
        finally:
            for h in hooks:
                h.remove()

        if not attention_tensors:
            raise RuntimeError("No attention tensors captured")

        stacked = torch.stack(attention_tensors)  # [15, N, 24, 64, 64]
        avg_attn = stacked.mean(dim=(0, 2))      # [N, 64, 64]

        files = "abcdefgh"
        ranks = "12345678"
        results = []

        for b_idx in range(len(fens)):
            vec = avg_attn[b_idx].mean(dim=0)     # mean over queries -> [64]
            max_val = vec.max()
            min_val = vec.min()
            if max_val > min_val:
                vec = (vec - min_val) / (max_val - min_val)
            else:
                vec = torch.zeros_like(vec)

            vec_list = vec.tolist()
            saliency_map = {
                f"{files[i % 8]}{ranks[i // 8]}": vec_list[i] for i in range(64)
            }

            if is_black_list[b_idx]:
                saliency_map = {
                    sq[0] + str(9 - int(sq[1])): v for sq, v in saliency_map.items()
                }

            results.append(saliency_map)

        return results

    def _saliency_absolute(self, board: "chess.Board") -> dict[str, float]:
        """
        BT3 attention for `board`, always keyed by TRUE absolute squares.

        _attention_saliency is only correct for white-to-move positions. For
        black-to-move positions LC0/BT3 works in the flipped side-to-move frame,
        so we evaluate the vertically-mirrored (white-to-move) board and flip the
        square keys back (rank r -> 9-r). Verified against the white-to-move map.
        """
        if board.turn == chess.WHITE:
            return self._attention_saliency(board.fen())
        mirrored = board.mirror()  # swaps colors + flips ranks -> white to move
        s = self._attention_saliency(mirrored.fen())
        return {sq[0] + str(9 - int(sq[1])): v for sq, v in s.items()}

    def calculation_saliency(
        self,
        root_board: "chess.Board",
        lines: list[dict],
        max_positions: int = 8,
        decay: float = 0.85,
    ) -> dict[str, float]:
        """
        Aggregate absolute-frame BT3 attention over the future positions along the
        engine's top PV lines. `lines` = [{"moves": [chess.Move, ...], "weight": float}, ...].
        Weighting: line weight * decay**ply. Deduplicates positions. Caps at
        max_positions total BT3 forwards (each ~1.5s). Returns a [0,1]-normalized map.
        """
        agg = {sq: 0.0 for sq in chess.SQUARE_NAMES}
        total_w = 0.0
        used = 0
        seen: set[str] = set()

        for line in sorted(lines, key=lambda ln: -ln.get("weight", 0.0)):
            if used >= max_positions:
                break
            board = root_board.copy()
            w = line.get("weight", 0.0)
            for ply, mv in enumerate(line.get("moves", [])):
                if used >= max_positions:
                    break
                try:
                    board.push(mv)
                except Exception:
                    break
                key = board.epd()
                if key in seen:
                    continue
                seen.add(key)
                weight = w * (decay ** ply)
                s = self._saliency_absolute(board)
                for sq, v in s.items():
                    agg[sq] += weight * v
                total_w += weight
                used += 1

        if total_w > 0:
            for sq in agg:
                agg[sq] /= total_w
        mx = max(agg.values()) if agg else 0.0
        if mx > 0:
            for sq in agg:
                agg[sq] /= mx
        return agg

    def _policy_fallback(self, fen: str, policy_dist: list[dict] = None) -> dict[str, float]:
        # Sum each move's p onto its from and to squares
        saliency_map = {f"{f}{r}": 0.0 for f in "abcdefgh" for r in "12345678"}
        if not policy_dist:
            return saliency_map
        for move in policy_dist:
            p = move.get("p", 0.0)
            frm = move.get("from")
            to = move.get("to")
            if frm in saliency_map: saliency_map[frm] += p
            if to in saliency_map: saliency_map[to] += p
        max_val = max(saliency_map.values()) if saliency_map else 0.0
        if max_val > 0:
            for sq in saliency_map: saliency_map[sq] /= max_val
        return saliency_map
