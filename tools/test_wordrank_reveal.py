import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bot import wordrank_game


async def main():
    game_id = await wordrank_game.new_game("reveal-diagnostic")
    print(f"game={game_id}")
    print(f"answer={await wordrank_game.reveal('reveal-diagnostic')}")


asyncio.run(main())
