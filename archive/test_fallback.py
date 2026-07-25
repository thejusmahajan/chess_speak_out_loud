import asyncio
import json
from backend.neural_vision import NeuralVision
from backend.engine_manager import LC0Engine

async def main():
    e = LC0Engine()
    await e.start()
    fen = 'r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1'
    policy_dist = await e.get_policy_distribution(fen, nodes=1)
    
    nv = NeuralVision(weights_path=r'C:\Users\Admin\Documents\chess_speak_out_loud\engine\791556.pb.gz')
    saliency = nv.saliency(fen, policy_dist=policy_dist)
    
    print("Fallback Saliency (top 10 squares):")
    # Sort and print
    sorted_s = sorted(saliency.items(), key=lambda x: x[1], reverse=True)
    for sq, val in sorted_s[:10]:
        print(f"{sq}: {val:.3f}")

asyncio.run(main())
