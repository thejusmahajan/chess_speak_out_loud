import asyncio
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.training.pipeline import run_diagnosis
from backend.training import store
from backend.engine_manager import LC0Engine
from backend.neural_vision import NeuralVision

async def main():
    pgn_text = ""
    for f_name in ["game_1_lc0_vs_sf.pgn", "game_2_lc0_vs_sf.pgn"]:
        path = os.path.join("scratch", f_name)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                pgn_text += f.read() + "\n\n"
                
    if not pgn_text:
        print("No PGN found.")
        return
        
    job_id = store.create_job()
    
    ENGINE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine")
    engine = LC0Engine(engine_path=os.path.join(ENGINE_DIR, "lc0.exe"))
    vision = NeuralVision(onnx_path=os.path.join(ENGINE_DIR, "bt3.onnx"))
    
    # Initialize singletons to start subprocesses/models
    print("Starting LC0...")
    await engine.start()
    await engine.analyze("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", depth=1)
    
    print("Starting diagnosis...")
    await run_diagnosis(job_id, pgn_text, "LC0", engine, vision)
    
    prof_path = os.path.join("data", "training", "profile.json")
    if os.path.exists(prof_path):
        print("Profile generated.")
        with open(prof_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
            
        print(f"Findings count: {len(profile['findings'])}")
        if profile['findings']:
            print("First finding:")
            print(json.dumps(profile['findings'][0], indent=2))
            
        print("Aggregates:")
        print(json.dumps(profile['aggregates'], indent=2))
    else:
        print("Error: No profile.json found.")
        job = store.read_job(job_id)
        print("Job error:", job.get("error"))

if __name__ == "__main__":
    asyncio.run(main())
