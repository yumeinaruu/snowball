from aiogram import types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import ReplyKeyboardRemove

from src.snowball.handlers_fcm.steps import available_type_choices, available_chat_choices
from .fsm import make_row_keyboard, Register
from .routers import snowball_router
import logging


# @snowball_router.message(Command("start"))
# async def start(
#         message: types.Message
# ):
#     msg = """
#     Сосал?
#     """
#     await message.answer(msg)


# @snowball_router.message(Command("register"))
@snowball_router.message(StateFilter(None), Command("start"))
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


@snowball_router.message(
    Register.choosing_register,
    F.text.in_(available_type_choices)
)
async def start_type_chosen(message: types.Message, state: FSMContext):
    await state.update_data(chosen_start_type=message.text.lower())
    if message.text.lower() == "регистрация":
        await message.answer(
            text="Теперь выбери название чата:",
            reply_markup=make_row_keyboard(available_chat_choices)
        )
        await state.set_state(Register.choosing_chat_options)
    elif message.text.lower() == "отправка сообщения":
        await message.answer(
            text="do u suck?",
            reply_markup=make_row_keyboard(['да', 'нет'])
        )
        await state.set_state(Register.choosing_chat_options)


@snowball_router.message(Register.choosing_register)
async def choice_incorrect(message: types.Message):
    await message.answer_sticker(
        r'CAACAgIAAxkBAAEKu_hnVFXyusZgy9KLwB7A3Z7cDqt1DgACEiAAAmd5uUhgfmY8HebIQDYE'
    )
    await message.answer(
        text="Нет такой опции(.\n\n"
             "Выбери одну из списка ниже:",
        reply_markup=make_row_keyboard(available_type_choices)
    )


@snowball_router.message(Register.choosing_chat_options, F.text.in_(available_chat_choices))
async def food_size_chosen(message: types.Message, state: FSMContext):
    await message.answer(
        text=f"Ты выбрал чат {message.text.lower()}.\n"
             f"Теперь напиши свою роль",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@snowball_router.message(Register.choosing_chat_options)
async def choice_incorrect_chat(message: types.Message):
    await message.answer_sticker(
        r'CAACAgIAAxkBAAEKu_hnVFXyusZgy9KLwB7A3Z7cDqt1DgACEiAAAmd5uUhgfmY8HebIQDYE'
    )
    await message.answer(
        text="Нет такого чата(.\n\n"
             "Выбери один из списка ниже:",
        reply_markup=make_row_keyboard(available_chat_choices)
    )


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
    # await message.answer("Ну ты и уёба")


@snowball_router.message(StateFilter(None), Command(commands=["cancel"]))
@snowball_router.message(default_state, F.text.lower() == "отмена")
async def cmd_cancel_no_state(message: types.Message, state: FSMContext):
    await state.set_data({})
    await message.answer(
        text="Нечего отменять",
        reply_markup=ReplyKeyboardRemove()
    )


@snowball_router.message(Command(commands=["cancel"]))
@snowball_router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=ReplyKeyboardRemove()
    )