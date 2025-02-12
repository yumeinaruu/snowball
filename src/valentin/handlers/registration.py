from aiogram import types, F, Router
from aiogram.filters import StateFilter
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from src.models import User
from src.utils.db import session
from src.valentin.fsm import RegisterState, StateStart
from src.valentin.keyboards import make_row_keyboard
from .utils import available_course_choices, available_type_choices_dict


reg_router = Router()


@reg_router.message(StateFilter(StateStart.starting), F.text == available_type_choices_dict['reg'])
async def registration_start_chosen(message: types.Message, state: FSMContext):
    if User.is_exists(message.from_user.id):
        await message.answer("Ти вже зареєстрований")
        return

    await message.answer(
        text="Тепер вибери курс:",
        reply_markup=make_row_keyboard(available_course_choices)
    )
    await state.set_state(RegisterState.choose_course)


@reg_router.message(StateFilter(RegisterState.choose_course), F.text.in_(available_course_choices))
async def registration_course_chosen(message: types.Message, state: FSMContext):
    await message.answer(
        text=f"Ти вибрав курс {message.text.lower()}.\n"
             f"Тепер напиши своє ім'я",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.update_data({"course": message.text})
    await state.set_state(RegisterState.choose_name)


@reg_router.message(StateFilter(RegisterState.choose_course), F.text.not_in_(available_course_choices))
async def registration_course_incorrect(message: types.Message):
    await message.answer(
        text="Немає такого курсу\n\n"
             "Вибери один зі списку нижче:",
        reply_markup=make_row_keyboard(available_course_choices)
    )


@reg_router.message(StateFilter(RegisterState.choose_name))
async def registration_choosing_name(message: types.Message, state: FSMContext):
    await state.update_data({"name": message.text.capitalize()})
    data = await state.get_data()
    try:
        user = User(tg_id=message.from_user.id, name=data["name"], course=data["course"])
        session.add(user)
        session.commit()
        await message.answer(f"{data["name"]}!")
        await state.clear()
    except Exception:
        session.rollback()
        await state.clear()
        await message.answer(f"ПОМИЛКА! Поскаржтеся розробнику! \n\n{e}")
