"""
UCI Engine Wrapper for LC0 (Leela Chess Zero).

Provides an async-friendly interface to the LC0 chess engine using
python-chess's SimpleEngine.popen_uci(). Falls back to mock mode
when the engine binary is not available.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Optional

import chess
import chess.engine

from backend.mock_data import get_mock_analysis

logger = logging.getLogger(__name__)

# Default engine directory
ENGINE_DIR = Path(r"C:\Users\Admin\Documents\chess_speak_out_loud\engine")


class LC0Engine:
    """
    Wrapper around the LC0 UCI chess engine.

    If the engine binary is not found or fails to start, the engine
    transparently falls back to mock mode, returning pre-computed
    analysis from the mock_data module.
    """

    def __init__(
        self,
        engine_path: Optional[str] = None,
        weights_path: Optional[str] = None,
    ) -> None:
        """
        Initialize the engine wrapper.

        Args:
            engine_path: Absolute path to the lc0.exe binary.
                         Defaults to ENGINE_DIR / "lc0.exe".
            weights_path: Absolute path to the .pb.gz weights file.
                          If None, LC0 will use its default weights.
        """
        self.engine_path: Path = Path(engine_path) if engine_path else ENGINE_DIR / "lc0.exe"
        self.weights_path: Optional[Path] = Path(weights_path) if weights_path else None
        self.engine: Optional[chess.engine.SimpleEngine] = None
        self.mock_mode: bool = False
        self._lock: asyncio.Lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """
        Start the UCI engine subprocess.

        If the engine binary does not exist or fails to launch, the
        engine silently enters mock mode so the rest of the application
        can continue to function.
        """
        if not self.engine_path.exists():
            logger.warning(
                "Engine binary not found at %s — entering mock mode.",
                self.engine_path,
            )
            self.mock_mode = True
            return

        try:
            # Build UCI options
            uci_options: dict = {
                "UCI_ShowWDL": True,
                "PerPVCounters": True
            }
            if self.weights_path and self.weights_path.exists():
                uci_options["WeightsFile"] = str(self.weights_path)

            # Auto-detect weights in the engine directory if not specified
            if not self.weights_path:
                weights_candidates = list(ENGINE_DIR.glob("*.pb.gz"))
                if weights_candidates:
                    uci_options["WeightsFile"] = str(weights_candidates[0])
                    logger.info("Auto-detected weights: %s", weights_candidates[0])

            # Start engine natively
            transport, engine = await chess.engine.popen_uci(str(self.engine_path))
            
            # Apply UCI options
            for key, value in uci_options.items():
                await engine.configure({key: value})
                
            self.engine = engine
            self.mock_mode = False
            logger.info("LC0 engine started successfully from %s", self.engine_path)

        except Exception as exc:
            logger.error("Failed to start engine: %s — entering mock mode.", exc)
            self.engine = None
            self.mock_mode = True

    async def stop(self) -> None:
        """Quit the engine subprocess cleanly."""
        if self.engine is not None:
            try:
                await self.engine.quit()
                logger.info("Engine stopped.")
            except Exception as exc:
                logger.warning("Error while stopping engine: %s", exc)
            finally:
                self.engine = None

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Return True if a real engine connection is active."""
        return self.engine is not None and not self.mock_mode

    async def analyze(
        self,
        fen: str,
        depth: int = 20,
        multipv: int = 3,
        time_limit: float = 2.0,
    ) -> dict:
        """
        Analyze a chess position. Acquires the engine lock and waits
        if another analysis is in progress.
        """
        if self.mock_mode or self.engine is None:
            return get_mock_analysis(fen)

        async with self._lock:
            return await self._do_analyze(fen, depth, multipv, time_limit)

    async def fast_analyze(
        self,
        fen: str,
        depth: int = 20,
        multipv: int = 1,
        time_limit: float = 1.0,
    ) -> dict:
        """
        Non-blocking analyze: if the engine is busy (lock held),
        immediately returns mock data instead of waiting.
        """
        if self.mock_mode or self.engine is None:
            return get_mock_analysis(fen)

        if self._lock.locked():
            logger.info("Engine busy — returning mock data for fast_analyze")
            return get_mock_analysis(fen)

        async with self._lock:
            return await self._do_analyze(fen, depth, multipv, time_limit)

    async def _do_analyze(
        self,
        fen: str,
        depth,
        multipv: int,
        time_limit: float,
    ) -> dict:
        """Internal: run the actual engine analysis. Caller must hold _lock."""
        try:
            board = chess.Board(fen)
            limit_kwargs = {"time": time_limit}
            if depth is not None:
                limit_kwargs["depth"] = depth
            infos = await self.engine.analyse(
                board,
                chess.engine.Limit(**limit_kwargs),
                multipv=multipv,
            )
            
            if not isinstance(infos, list):
                infos = [infos]

            best_moves = []
            pv_lines = []
            evaluation = 0
            nodes = 0
            wdl = None

            for idx, info in enumerate(infos):
                score_obj = info.get("score")
                pv = info.get("pv", [])
                info_nodes = info.get("nodes", 0)

                if score_obj is not None:
                    pov_score = score_obj.white()
                    if pov_score.is_mate():
                        score_cp = f"M{pov_score.mate()}"
                    else:
                        score_cp = pov_score.score()
                else:
                    score_cp = 0

                wdl_obj = info.get("wdl")
                info_wdl = None
                if wdl_obj is not None:
                    try:
                        info_wdl = [wdl_obj.white().wins, wdl_obj.white().draws, wdl_obj.white().losses]
                    except Exception:
                        info_wdl = None

                if idx == 0:
                    evaluation = score_cp
                    nodes = info_nodes
                    wdl = info_wdl

                if pv:
                    move = pv[0]
                    san = board.san(move)
                    best_moves.append({
                        "move": move.uci(),
                        "san": san,
                        "score": score_cp,
                        "nodes": info_nodes,
                        "wdl": info_wdl
                    })

                    pv_san_parts = []
                    temp_board = board.copy()
                    for m in pv:
                        try:
                            pv_san_parts.append(temp_board.san(m))
                            temp_board.push(m)
                        except Exception:
                            break
                    pv_lines.append(" ".join(pv_san_parts))

            return {
                "evaluation": evaluation,
                "best_moves": best_moves,
                "pv_lines": pv_lines,
                "nodes": nodes,
                "wdl": wdl,
            }

        except Exception as exc:
            logger.error("Engine analysis failed: %s — falling back to mock.", exc)
            return get_mock_analysis(fen)
