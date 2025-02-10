import asyncio
import logging
from src.args_parser import args
from src.bot import bot

logging.basicConfig(level=logging.INFO)


async def run_server():
    await bot.run()


if __name__ == "__main__":
    if args.create_db:
        from src.utils.db import create_tables

        create_tables()

    asyncio.run(run_server())
