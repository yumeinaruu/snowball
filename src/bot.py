from aiogram import Bot, Dispatcher
from src.settings import settings
from src.valentin.handlers import messages, registration, main


class ValentinBot:
    async def run(self):
        valentin_bot = Bot(token=settings.BOT_TOKEN)
        dp = Dispatcher()

        dp.include_routers(registration.reg_router, messages.messages_router, main.main_router)

        await valentin_bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(valentin_bot)


bot = ValentinBot()
