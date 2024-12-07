from aiogram import types
from aiogram.filters import Command
from .routers import snowball_router


@snowball_router.message(Command("start"))
async def start(
        message: types.Message
):
    await message.answer("Hi!")
