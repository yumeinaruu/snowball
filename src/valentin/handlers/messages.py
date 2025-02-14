from datetime import datetime
from random import randint

from aiogram import types, F, Router
from aiogram.types import ReplyKeyboardRemove
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.models import User, Message
from src.utils.db import session
from src.valentin.fsm import StateStart, SendingMessageState, UserCallbackFactory
from src.valentin.keyboards import make_row_keyboard, generate_prev_stop_next_keyboard
from src.utils.constans import all_predictions
from .utils import available_course_choices, available_type_choices_dict

messages_router = Router()


@messages_router.message(StateFilter(StateStart.starting), F.text == available_type_choices_dict['send'])
async def sending_message_start(message: types.Message, state: FSMContext):
    user = User.get_by_tg_id(message.from_user.id)
    if user:
        await message.answer(
            text="Тепер вибери курс:",
            reply_markup=make_row_keyboard(available_course_choices)
        )
        await state.set_state(SendingMessageState.choose_course)
        return
    await message.answer("Ти ще не зареєстрований")


@messages_router.message(StateFilter(SendingMessageState.choose_course), F.text.in_(available_course_choices))
async def sending_message_course_chosen(message: types.Message, state: FSMContext):
    await message.answer(
        text=f"Ваш вибір: {message.text.lower()}.\n"
             f"Тепер вибери людину",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.update_data({"course": message.text.capitalize()})
    await state.set_state(SendingMessageState.choose_receiver)

    users = User.get_by_course(course=(await state.get_data())["course"])
    msg = "Список людей:"
    builder = InlineKeyboardBuilder()
    for user in users:
        builder.button(text=f"{user.name}", callback_data=UserCallbackFactory(telegram_id=user.tg_id))

    await message.answer(
        text=msg,
        reply_markup=builder.adjust(5).as_markup()
    )


@messages_router.callback_query(StateFilter(SendingMessageState.choose_receiver), UserCallbackFactory.filter())
async def sending_message_receiver_chosen(callback: types.CallbackQuery, callback_data: UserCallbackFactory,
                                          state: FSMContext):
    await callback.message.answer("Тепер напиши валентинку")
    await state.update_data({"to_user": callback_data.telegram_id})
    await state.set_state(SendingMessageState.choose_message)


@messages_router.message(StateFilter(SendingMessageState.choose_message))
async def sending_message_message_chosen(message: types.Message, state: FSMContext):
    to_user_obj = User.get_by_tg_id((await state.get_data())["to_user"])
    try:
        msg = Message(text=message.text,
                      from_user=User.get_by_tg_id(message.from_user.id),
                      to_user=to_user_obj)
        session.add(msg)
        session.commit()
        await message.answer(f"Вашу валентинку прийнято. Рівно о 13:00 14 лютого людина її отримає {to_user_obj.name} з {to_user_obj.course} групи! 💞.\nА поки ви чекаєте, отримайте від нас невелике побажання:")
        await message.answer(all_predictions[randint(0, len(all_predictions) - 1)])
        await state.clear()
        await state.set_data({})
    except Exception as e:
        session.rollback()
        await state.clear()
        await message.answer(f"ПАМИЛКА! Поскаржтеся розробнику! \n\n{e}")


@messages_router.message(StateFilter(None), Command("valentin"))
async def watch_valentin(message: types.Message, state: FSMContext):
    if datetime.now() >= datetime(2025, 2, 14, 12, 00, 00):
        messages_count = Message.get_count_messages_to_user(User.get_by_tg_id(message.from_user.id).id)
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(
            text="Переглянути валентинку",
            callback_data="valentinmessages_start"),
        )
        if messages_count > 0:
            await message.answer(f"{messages_count} людей відправили вам валентинки! Бажаєте їх переглянути? 💞",
                                 reply_markup=builder.as_markup())
        else:
            await message.answer(
                f"Вам не надіслали валентинку(\nТримайте натомість передбачення від нас: {all_predictions[randint(0, len(all_predictions) - 1)]}")
    else:
        await message.answer("Час ще не настав...")


id_messages = {}


@messages_router.callback_query(F.data.startswith("valentinmessages_"))
async def callbacks_num(callback: types.CallbackQuery):
    message_id = id_messages.get(callback.from_user.id, 0)
    action = callback.data.split("_")[1]
    messages = Message.get_messages_to_user(User.get_by_tg_id(callback.from_user.id).id)

    if messages:
        try:
            count_messages = messages.count()
            prev_flag = True if message_id > 0 else False
            next_flag = True if message_id < count_messages - 1 else False
            if action == "start":
                id_messages[callback.from_user.id] = 0
                keyboard = generate_prev_stop_next_keyboard(prev=prev_flag, next=next_flag)
                await callback.message.edit_text(messages[0].text, reply_markup=keyboard.as_markup())
            if action == "prev":
                id_messages[callback.from_user.id] = message_id - 1 if message_id > 0 else 0
                keyboard = generate_prev_stop_next_keyboard(prev=prev_flag, next=next_flag)
                await callback.message.edit_text(messages[message_id].text, reply_markup=keyboard.as_markup())
            elif action == "next":
                id_messages[callback.from_user.id] = message_id + 1 if message_id < count_messages - 1 else count_messages - 1
                keyboard = generate_prev_stop_next_keyboard(prev=prev_flag, next=next_flag)
                await callback.message.edit_text(messages[message_id].text, reply_markup=keyboard.as_markup())
            elif action == "end":
                id_messages.pop(callback.from_user.id)
                await callback.message.edit_text(f"Закінчилися валентинки")
        except Exception as e:
            await callback.answer(f"ПАМИЛКА! Поскаржтеся розробнику! \n\n{e}")
    else:
        await callback.message.edit_text(
            f"Вам не прислали валентинку(\nДержите в замен предсказание от нас: {all_predictions[randint(0, len(all_predictions) - 1)]}")
