import logging
from aiogram import types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.models import Users, Messages
from src.utils.db import session
from src.snowball.handlers_fcm.steps import available_type_choices, available_chat_choices
from .fsm import make_row_keyboard, Register, UserCallbackFactory
from .routers import snowball_router


@snowball_router.message(StateFilter(None), Command(commands=["cancel"]))
@snowball_router.message(default_state, F.text.lower() == "отмена")
async def cmd_cancel_no_state(message: types.Message, state: FSMContext):
    await state.set_data({})
    await message.answer(
        text="Нечего отменять",
        reply_markup=ReplyKeyboardRemove()
    )


@snowball_router.message(Command(commands=["cancel"]) or F.text.lower() == "отмена")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=ReplyKeyboardRemove()
    )


@snowball_router.message(StateFilter(None), Command(commands=["start", "menu"]))
async def menu(
        message: types.Message,
        state: FSMContext
):
    await message.answer(
        text="Что вы хотите сделать?",
        reply_markup=make_row_keyboard(available_type_choices)
    )
    await state.set_state(Register.choosing_register)


@snowball_router.message(
    Register.choosing_register,
    F.text.in_(available_type_choices)
)
async def start_type_chosen(message: types.Message, state: FSMContext):
    await state.update_data(chosen_start_type=message.text.lower())
    if message.text.lower() == "регистрация":
        user = Users.get_user_by_tg_id(message.from_user.id)
        if user:
            await message.answer("Ты уже зареган(")
        else:
            await message.answer(
                text="Теперь выбери название чата:",
                reply_markup=make_row_keyboard(available_chat_choices)
            )
            await state.set_state(Register.choosing_chat_options)
    elif message.text.lower() == "отправка сообщения":
        user = Users.get_user_by_tg_id(message.from_user.id)
        if user:
            await message.answer(
                text="Теперь выбери название чата:",
                reply_markup=make_row_keyboard(available_chat_choices)
            )
            await state.set_state(Register.choosing_chat_options)
        else:
            await message.answer("Ты еще не зареган(")


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
async def chat_type_chosen(message: types.Message, state: FSMContext):
    if (await state.get_data())["chosen_start_type"] == "отправка сообщения":
        await message.answer(
            text=f"Ты выбрал чат {message.text.lower()}.\n"
                 f"Теперь выбери пользователя",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.update_data({"chat": message.text.capitalize()})
        await state.set_state(Register.choosing_receiver)

        users = session.query(Users).filter_by(chat=(await state.get_data())["chat"]).all()
        msg = "Пользователи:"
        builder = InlineKeyboardBuilder()
        for user in users:
            builder.button(text=f"{user.role}", callback_data=UserCallbackFactory(telegram_id=user.tg_id))

        await message.answer(
            text=msg,
            reply_markup=builder.as_markup()
        )
    if (await state.get_data())["chosen_start_type"] == "регистрация":
        await message.answer(
            text=f"Ты выбрал чат {message.text.lower()}.\n"
                 f"Теперь напиши свою роль",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.update_data({"chat": message.text.capitalize()})
        await state.set_state(Register.choosing_role)


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


@snowball_router.message(Register.choosing_role)
async def choosing_role(message: types.Message, state: FSMContext):
    await state.update_data({"role": message.text.capitalize()})
    data = await state.get_data()
    user = Users(tg_id=message.from_user.id, role=data["role"], chat=data["chat"])
    session.add(user)
    session.commit()
    await message.answer(f"{data["role"]} юпиё!")
    await state.clear()
    await state.set_data({})


@snowball_router.callback_query(Register.choosing_receiver, UserCallbackFactory.filter())
async def chat_choose_receiver(callback: types.CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext):
    await callback.message.answer("Напиши пожелание для участника) ")
    await state.update_data({"to_user": callback_data.telegram_id})
    await state.set_state(Register.choosing_message)


@snowball_router.callback_query(StateFilter(None), F.data == "user_chosen")
async def chat_choose_receiver_without_state(message: types.Message):
    await message.answer("Жулик, не делай так.")


@snowball_router.callback_query(Register.choosing_message, UserCallbackFactory.filter())
async def chat_choosing_message(message: types.Message, state: FSMContext):
    to_user_obj = Users.get_user_by_tg_id((await state.get_data())["to_user"])
    msg = Messages(text=message.text, from_user=Users.get_user_by_tg_id(message.from_user.id),
                   to_user=to_user_obj)
    session.add(msg)
    session.commit()
    await message.answer(f"Юпиёёёёё!\nСообщение отправлено участнику {to_user_obj.role} из {to_user_obj.chat}")
    await state.clear()
    await state.set_data({})


@snowball_router.callback_query(Register.choosing_receiver, F.data == "prev_page_users")
async def chat_choose_receiver(message: types.Message, state: FSMContext):
    await message.answer("HUI")


@snowball_router.callback_query(Register.choosing_receiver, F.data == "next_page_users")
async def chat_choose_receiver(message: types.Message, state: FSMContext):
    await message.answer("HUI")


@snowball_router.message(Command("me"))
async def me(message: types.Message):
    user = Users.get_user_by_tg_id(tg_id=message.from_user.id)
    if user:
        await message.answer(f"Ты {user.role}\nИ твой чат {user.chat}")
    else:
        await message.answer("Ты не зареган")


@snowball_router.message()
async def all_messages(
        message: types.Message
):
    logging.info(f"{message.from_user.first_name}(@{message.from_user.username}): {message.text}")
