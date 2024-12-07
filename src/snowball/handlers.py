from aiogram import types
from aiogram.filters import Command
from .routers import snowball_router


@snowball_router.message(Command("start"))
async def start(
        message: types.Message
):
    msg = """
    """
    await message.answer(msg)


@snowball_router.message(Command("register"))
async def register(
        message: types.Message
):
    await message.answer(str(message.from_user))


@snowball_router.message(Command("send"))
async def send(
        message: types.Message
):
    await message.answer(str(message.from_user))