import asyncio
import logging
from aiogram import Bot, Dispatcher
from src.settings import settings
from src.snowball.handlers_fcm import snowball_router


logging.basicConfig(level=logging.INFO)


async def run_server():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_routers(snowball_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_server())