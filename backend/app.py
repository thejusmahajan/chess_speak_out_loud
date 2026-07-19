"""
Chess Speak Out Loud — FastAPI Application.

Serves the frontend static files and provides REST API endpoints for:
  - Position analysis (engine + heatmaps + concept mapping)
  - PGN analysis (per-move breakdown)
  - Health check
"""

import asyncio
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
from backend.neural_vision import NeuralVision
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
neural_vision = NeuralVision(onnx_path=str(ENGINE_DIR / "bt3.onnx"))


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

    # Get Neural Vision / Saliency (Phase 2)
    saliency = neural_vision.saliency(fen, policy_dist=policy_dist)

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
        "policy": policy_dist[:20],
        "saliency": saliency,
        "saliency_source": neural_vision.mode
    }


@app.post("/api/calculation-glow")
async def calculation_glow(request: AnalyzeRequest):
    """
    Compute the aggregated 'Calculation Glow' for a position: BT3 attention
    averaged over the engine's top PV lines, weighted by line strength and depth.
    Expensive (~10-15s). Falls back to the single-position saliency if the engine
    is in mock mode or produced no lines.
    """
    fen = request.fen.strip()
    try:
        board = chess.Board(fen)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid FEN: {exc}")

    lines = await lc0_engine.search_lines(
        fen, time_limit=request.time_limit, multipv=request.multipv
    )
    if not lines:
        # mock mode or no search result -> just return the intuition map
        policy_dist = await lc0_engine.get_policy_distribution(fen, nodes=1)
        return {
            "fen": fen,
            "calculation_saliency": neural_vision.saliency(fen, policy_dist=policy_dist),
            "positions_used": 0,
            "saliency_source": neural_vision.mode,
        }

    calc = await asyncio.to_thread(
        neural_vision.calculation_saliency, board, lines
    )
    return {
        "fen": fen,
        "calculation_saliency": calc,
        "positions_used": min(8, sum(len(l["moves"]) for l in lines)),
        "saliency_source": neural_vision.mode,
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
# Elite Training System endpoints (Gemini-owned)
# ------------------------------------------------------------------

from backend.training.pipeline import run_diagnosis
from backend.training import store, drills
import asyncio
import json

class DiagnoseRequest(BaseModel):
    pgn: str
    player_name: str

class RepertoireRequest(BaseModel):
    color: str

class GenerateDrillsRequest(BaseModel):
    count: int = 20

class AttemptDrillRequest(BaseModel):
    set_id: str
    drill_id: str
    move_uci: str

@app.post("/api/training/diagnose")
async def start_diagnose(req: DiagnoseRequest):
    import os
    jobs_dir = Path(store.DATA_DIR) / "jobs"
    if jobs_dir.exists():
        for job_file in jobs_dir.glob("*.json"):
            with open(job_file, "r") as f:
                j = json.load(f)
                if j.get("status") == "running":
                    raise HTTPException(status_code=409, detail="A diagnosis job is already running")
                    
    job_id = store.create_job()
    asyncio.create_task(run_diagnosis(job_id, req.pgn, req.player_name, lc0_engine, neural_vision))
    return {"job_id": job_id}

@app.get("/api/training/jobs/{job_id}")
async def get_job(job_id: str):
    job = store.read_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/api/training/profile")
async def get_profile():
    profile = store.load_profile()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@app.post("/api/training/repertoire")
async def get_repertoire(req: RepertoireRequest):
    rep = store.load_repertoire()
    if not rep:
        return {}
    return rep

@app.post("/api/training/drills/generate")
async def generate_drills_ep(req: GenerateDrillsRequest):
    profile = store.load_profile()
    repertoire = store.load_repertoire()
    drill_set = await drills.generate_drill_set(req.count, profile, repertoire, lc0_engine, neural_vision)
    return drill_set

@app.get("/api/training/drills")
async def list_drills():
    return store.list_drill_sets()

@app.get("/api/training/drills/{set_id}")
async def get_drill_set(set_id: str):
    ds = store.load_drill_set(set_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Drill set not found")
    
    import copy
    cloned = copy.deepcopy(ds)
    for d in cloned.get("drills", []):
        if "reveal" in d:
            del d["reveal"]
    return cloned

@app.post("/api/training/drills/attempt")
async def attempt_drill(req: AttemptDrillRequest):
    ds = store.load_drill_set(req.set_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Drill set not found")
    
    for d in ds.get("drills", []):
        if d["id"] == req.drill_id:
            correct = req.move_uci in d.get("alt_solution_ucis", [])
            return {"correct": correct, "reveal": d.get("reveal")}
            
    raise HTTPException(status_code=404, detail="Drill not found")



# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
