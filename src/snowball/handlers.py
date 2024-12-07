from aiogram import types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from src.snowball.handlers.steps import available_type_choices
from .fsm import make_row_keyboard, Register
from .routers import snowball_router
import logging


@snowball_router.message(Command("start"))
async def start(
        message: types.Message
):
    msg = """
    Сосал?
    """
    await message.answer(msg)


# @snowball_router.message(Command("register"))
@snowball_router.message(StateFilter(None), Command("register"))
async def register(
        message: types.Message,
        state: FSMContext
):
    await message.answer(
        text="Что вы хотите сделать?",
        reply_markup=make_row_keyboard(available_type_choices)
    )
    await state.set_state(Register.choosing_register)
    # await message.answer(str(message.from_user))


@snowball_router.message(Command("send"))
async def send(
        message: types.Message
):
    await message.answer(str(message.from_user))


@snowball_router.message()
async def all_messages(
        message: types.Message
):
    logging.info(message.text)
    await message.answer("Ну ты и уёба")