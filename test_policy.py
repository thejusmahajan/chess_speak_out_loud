import asyncio
from backend.engine_manager import LC0Engine
async def main():
    e = LC0Engine()
    await e.start()
    policies = await e.get_policy_distribution('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', nodes=1)
    import pprint
    pprint.pprint(policies[:5])
asyncio.run(main())
