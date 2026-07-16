import asyncio
import chess
import chess.engine

async def main():
    transport, engine = await chess.engine.popen_uci(['C:/Users/Admin/Documents/chess_speak_out_loud/engine/lc0.exe', '--weights=C:/Users/Admin/Documents/chess_speak_out_loud/engine/791556.pb.gz'])
    await engine.configure({'VerboseMoveStats': True})
    board = chess.Board()
    with await engine.analysis(board, chess.engine.Limit(nodes=1)) as analysis:
        async for info in analysis:
            if 'string' in info:
                print('INFO STRING:', info['string'])
    await engine.quit()

asyncio.run(main())
