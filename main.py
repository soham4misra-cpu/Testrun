import asyncio

import pygame  # noqa: F401  (pygbag scans main.py's imports to know what to fetch)

from engine import Game


async def main():
    await Game().run()


if __name__ == "__main__":
    asyncio.run(main())
