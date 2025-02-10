from aiogram import types, F, Router
from aiogram.types import ReplyKeyboardRemove
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.models import Users, Messages
from src.utils.db import session
from src.valentin.fsm import StateStart, SendingMessageState, UserCallbackFactory
from src.valentin.keyboards import make_row_keyboard
from .utils import available_course_choices, available_type_choices_dict

messages_router = Router()


@messages_router.message(StateFilter(StateStart.starting), F.text == available_type_choices_dict['send'])
async def sending_message_start(message: types.Message, state: FSMContext):
    user = Users.get_by_tg_id(message.from_user.id)
    if user:
        await message.answer(
            text="Теперь выбери курс:",
            reply_markup=make_row_keyboard(available_course_choices)
        )
        await state.set_state(SendingMessageState.choose_course)
        return
    await message.answer("Ты еще не зареган(")


@messages_router.message(StateFilter(SendingMessageState.choose_course), F.text.in_(available_course_choices))
async def sending_message_course_chosen(message: types.Message, state: FSMContext):
    await message.answer(
        text=f"Ваш выбор: {message.text.lower()}.\n"
             f"Теперь выбери человека",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.update_data({"course": message.text.capitalize()})
    await state.set_state(SendingMessageState.choose_receiver)

    users = Users.get_by_course(course=(await state.get_data())["course"])
    msg = "Люди:"
    builder = InlineKeyboardBuilder()
    for user in users:
        builder.button(text=f"{user.name}", callback_data=UserCallbackFactory(telegram_id=user.tg_id))

    await message.answer(
        text=msg,
        reply_markup=builder.adjust(5).as_markup()
    )


@messages_router.callback_query(StateFilter(SendingMessageState.choose_receiver), UserCallbackFactory.filter())
async def sending_message_receiver_chosen(callback: types.CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext):
    await callback.message.answer("Напиши валентинку")
    await state.update_data({"to_user": callback_data.telegram_id})
    await state.set_state(SendingMessageState.choose_message)


@messages_router.message(StateFilter(SendingMessageState.choose_message))
async def sending_message_message_chosen(message: types.Message, state: FSMContext):
    to_user_obj = Users.get_by_tg_id((await state.get_data())["to_user"])
    try:
        msg = Messages(text=message.text,
                       from_user=Users.get_by_tg_id(message.from_user.id),
                       to_user=to_user_obj)
        session.add(msg)
        session.commit()
        await message.answer(f"Твое сообщение отправлено {to_user_obj.name} из {to_user_obj.course} группы.")
        await state.clear()
        await state.set_data({})
    except Exception:
        session.rollback()
        await message.answer("ОШИБКА! Пожалуйтесь разработчику")

