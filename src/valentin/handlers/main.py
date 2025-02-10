import logging
from aiogram import types, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from src.models import Users
from src.valentin.keyboards import make_row_keyboard
from src.valentin.fsm import StateStart
from .utils import available_type_choices, available_type_choices_dict

main_router = Router()


@main_router.message(F.text.lower() == "отмена", Command(commands=["cancel"]))
async def cmd_cancel_no_state(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=ReplyKeyboardRemove()
    )


@main_router.message(StateFilter(None), Command(commands=["start", "menu"]))
async def menu(message: types.Message, state: FSMContext):
    await message.answer(
        text="Что вы хотите сделать?",
        reply_markup=make_row_keyboard(available_type_choices)
    )
    await state.set_state(StateStart.starting)


@main_router.message(Command("me"))
async def me(message: types.Message, state: FSMContext):
    user = Users.get_by_tg_id(tg_id=message.from_user.id)
    await state.clear()
    if user:
        await message.answer(f"Ты {user.name}\nТвой курс: {user.course}")
    else:
        await message.answer("Ты не зареган")


@main_router.message(StateStart.starting, F.text.not_in(list(available_type_choices_dict.values())))
async def choice_incorrect(message: types.Message):
    await message.answer(
        text="Нет такой опции(.\n\n"
             "Выбери одну из списка ниже:",
        reply_markup=make_row_keyboard(available_type_choices)
    )


@main_router.message()
async def all_messages(message: types.Message, state: FSMContext):
    logging.info(f"{message.from_user.first_name}(@{message.from_user.username}): {message.text}. State: {await state.get_state()}")
    if await state.get_state() is None:
        await message.answer("Напишите /menu для вызова меню.")
