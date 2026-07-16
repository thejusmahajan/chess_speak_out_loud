"""
Chess Speak Out Loud — FastAPI Application.

Serves the frontend static files and provides REST API endpoints for:
  - Position analysis (engine + heatmaps + concept mapping)
  - PGN analysis (per-move breakdown)
  - Health check
"""

import io
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import chess
import chess.pgn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from dotenv import load_dotenv
load_dotenv()

import chess
from backend.engine_manager import LC0Engine
from backend.heatmap import generate_all_heatmaps
from backend.concept_mapper import analyze_position
from backend.mock_data import get_coach_summary
from backend.llm_client import generate_conversation

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

VERSION = "0.1.0"
LLM_ENABLED = False  # Aim: bypass all text-generation. Keep code dormant, never call at runtime.

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_DIR / "frontend"
ENGINE_DIR = PROJECT_DIR / "engine"

logger = logging.getLogger("chess_speak_out_loud")
logging.basicConfig(level=logging.INFO)

# ------------------------------------------------------------------
# Engine singleton
# ------------------------------------------------------------------

lc0_engine = LC0Engine(
    engine_path=str(ENGINE_DIR / "lc0.exe"),
)


# ------------------------------------------------------------------
# Lifespan
# ------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle for the FastAPI app."""
    logger.info("Starting Chess Speak Out Loud backend v%s", VERSION)
    await lc0_engine.start()
    if lc0_engine.is_available():
        logger.info("LC0 engine is LIVE.")
    else:
        logger.info("LC0 engine not found — running in MOCK mode.")
    yield
    # Shutdown
    await lc0_engine.stop()
    logger.info("Backend shut down.")


# ------------------------------------------------------------------
# App setup
# ------------------------------------------------------------------

app = FastAPI(
    title="Chess Speak Out Loud",
    version=VERSION,
    description="A chess training tool that teaches you to think out loud like a GM.",
    lifespan=lifespan,
)

# CORS — allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend static directories
if FRONTEND_DIR.exists():
    app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")
    app.mount("/lib", StaticFiles(directory=str(FRONTEND_DIR / "lib")), name="lib")
else:
    logger.warning("Frontend directory not found at %s", FRONTEND_DIR)


# ------------------------------------------------------------------
# Request / Response schemas
# ------------------------------------------------------------------

from typing import Optional
class AnalyzeRequest(BaseModel):
    """Request body for single-position analysis."""
    fen: str
    depth: Optional[int] = Field(default=None, ge=1, le=100)
    multipv: int = Field(default=3, ge=1, le=10)
    time_limit: float = Field(default=2.0, ge=0.1, le=300.0)
    # llm_model: Optional[str] = "gemini-3.5-flash"  # Disabled


class PGNRequest(BaseModel):
    """Request body for PGN analysis."""
    pgn: str


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------

@app.get("/", include_in_schema=False)
async def serve_index():
    """Serve the frontend index.html."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    raise HTTPException(
        status_code=404,
        detail="Frontend not found. Place index.html in the frontend/ directory.",
    )


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        status: "ok"
        engine_mode: "live" or "mock"
        version: application version string
    """
    return {
        "status": "ok",
        "engine_mode": "live" if lc0_engine.is_available() else "mock",
        "version": VERSION,
    }


@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    """
    Analyse a single chess position.

    Combines engine analysis, heatmap generation, and concept mapping
    into a single comprehensive response.

    Args:
        request: JSON body with ``fen``, ``depth``, ``multipv``.

    Returns:
        JSON with keys: fen, engine, heatmaps, concepts, coach_summary.
    """
    fen = request.fen.strip()

    # Validate FEN
    try:
        chess.Board(fen)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid FEN: {exc}")

    # Run engine analysis
    engine_result = await lc0_engine.analyze(
        fen=fen,
        depth=request.depth,
        multipv=request.multipv,
        time_limit=request.time_limit,
    )

    # Generate heatmaps
    heatmaps = generate_all_heatmaps(fen)
    
    # Generate projected heatmaps for the PV
    projected_heatmaps = []
    pv_lines = engine_result.get("pv_lines", [])
    if pv_lines:
        temp_board = chess.Board(fen)
        moves = pv_lines[0].split()
        for move_san in moves[:6]:
            try:
                temp_board.push_san(move_san)
                proj_hm = generate_all_heatmaps(temp_board.fen())
                projected_heatmaps.append({
                    "move": move_san,
                    "fen": temp_board.fen(),
                    "heatmaps": proj_hm
                })
            except Exception:
                break

    # Generate concept analysis
    concepts = analyze_position(fen, engine_analysis=engine_result)

    # LLM text-generation bypassed (Phase 0)
    # coach_summary = get_coach_summary(fen)
    # if coach_summary is None:
    #     coach_summary = await generate_conversation(...)

    # Format evaluation for frontend
    raw_eval = engine_result.get("evaluation", 0)
    if isinstance(raw_eval, str) and raw_eval.startswith("M"):
        eval_obj = {"type": "mate", "value": int(raw_eval[1:])}
    else:
        eval_obj = {"type": "cp", "value": int(raw_eval)}

    # Format best_moves for frontend
    frontend_moves = []
    for m in engine_result.get("best_moves", []):
        score = m.get("score", 0)
        if isinstance(score, str) and score.startswith("M"):
            eval_str = f"M{score[1:]}"
        else:
            eval_str = str(score)
        frontend_moves.append({
            "san": m.get("san"),
            "eval": eval_str,
            "score": score,
            "nodes": m.get("nodes"),
            "wdl": m.get("wdl")
        })

    # Get Policy Priors (Phase 1)
    policy_dist = await lc0_engine.get_policy_distribution(fen, nodes=1)

    return {
        "fen": fen,
        "evaluation": eval_obj,
        "best_moves": frontend_moves,
        "nodes": engine_result.get("nodes"),
        "wdl": engine_result.get("wdl"),
        "interpretation": {
            "observations": concepts.get("observations", [])
        },
        "heatmaps": heatmaps,
        "projected_heatmaps": projected_heatmaps,
        "policy": policy_dist[:20]
    }


@app.post("/api/play-move")
async def play_move(request: AnalyzeRequest):
    """
    Lightweight endpoint to simply get the engine's best move.
    Skips heatmap and concept generation for speed.
    """
    fen = request.fen.strip()

    try:
        chess.Board(fen)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid FEN: {exc}")

    # Run engine analysis quickly — non-blocking if engine is busy
    engine_result = await lc0_engine.fast_analyze(
        fen=fen,
        depth=None,
        multipv=1,
        time_limit=request.time_limit or 1.0,
    )

    best_moves = engine_result.get("best_moves", [])
    best_move = best_moves[0] if best_moves else None

    return {
        "fen": fen,
        "best_move": best_move
    }


@app.get("/api/live-game")
async def live_game():
    """
    Returns the FEN of the ongoing self-play match.
    Reads from scratch/live_game_fen.txt
    """
    fen_file = PROJECT_DIR / "scratch" / "live_game_fen.txt"
    if fen_file.exists():
        return {"fen": fen_file.read_text().strip()}
    return {"fen": None}


@app.post("/api/analyze-pgn")
async def analyze_pgn(request: PGNRequest):
    """
    Analyse an entire PGN game move-by-move.

    Parses the PGN, iterates through every position, and returns a
    list of per-position analyses.

    Args:
        request: JSON body with ``pgn`` string.

    Returns:
        JSON with keys: headers (PGN metadata), moves (list of
        per-move analysis dicts).
    """
    pgn_text = request.pgn.strip()
    if not pgn_text:
        raise HTTPException(status_code=400, detail="PGN string is empty.")

    try:
        game = chess.pgn.read_game(io.StringIO(pgn_text))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to parse PGN: {exc}")

    if game is None:
        raise HTTPException(status_code=400, detail="No game found in PGN.")

    # Extract headers
    headers = dict(game.headers)

    # Walk through the game
    board = game.board()
    moves_analysis = []

    for move_number, node in enumerate(game.mainline(), start=1):
        move = node.move
        san = board.san(move)

        # Analyse BEFORE the move is played
        fen_before = board.fen()

        engine_result = await lc0_engine.analyze(fen=fen_before, depth=15, multipv=1)
        heatmaps = generate_all_heatmaps(fen_before)
        concepts = analyze_position(fen_before, engine_analysis=engine_result)

        board.push(move)

        moves_analysis.append({
            "move_number": move_number,
            "san": san,
            "uci": move.uci(),
            "fen_before": fen_before,
            "fen_after": board.fen(),
            "engine": engine_result,
            "heatmaps": heatmaps,
            "concepts": concepts,
        })

    return {
        "headers": headers,
        "moves": moves_analysis,
    }


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
