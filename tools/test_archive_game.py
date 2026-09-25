import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bot import WordRankWebGame


async def main():
    game = WordRankWebGame()
    answer = await game.archive_answer("130")
    print(f"answer={answer}")
    result = await game.archive_guess("local-test", "130", "苹果")
    print(f"guess={result}")


asyncio.run(main())
