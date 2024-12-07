from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


class Register(StatesGroup):
    choosing_register = State()
    choosing_chat_options = State()
    choosing_user_options = State()
    choosing_role = State()
    choosing_receiver = State()
    choosing_message = State()