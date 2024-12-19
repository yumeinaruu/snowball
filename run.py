import asyncio
import logging
from aiogram import Bot, Dispatcher
from src.settings import settings
from src.args_parser import args
from src.snowball.handlers import snowball_router

logging.basicConfig(level=logging.INFO)


async def run_server():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_routers(snowball_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    if args.create_db:
        from src.utils.db import create_tables
        create_tables()

    asyncio.run(run_server())