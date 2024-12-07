import asyncio
from aiogram import Bot

from src.settings import settings
from src.utils.db import session
from src.models import Messages


async def main():
    messages = session.query(Messages).all()
    for message in messages:
        msg = f"От {message.from_user.role} из {message.from_user.chat}\n" + message.text
        while True:
            bot = Bot(token=settings.BOT_TOKEN)
            try:
                await bot.send_message(chat_id=message.to_user, text=msg)
            except Exception as e:
                print(f"{e}:  :(    ")
            finally:
                break

if __name__ == '__main__':
    asyncio.run(main())
