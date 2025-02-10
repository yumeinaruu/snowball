from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.callback_data import CallbackData


class StateStart(StatesGroup):
    starting = State()


class RegisterState(StatesGroup):
    choose_course = State()
    choose_name = State()


class SendingMessageState(StatesGroup):
    choose_course = State()
    choose_receiver = State()
    choose_message = State()


class UserCallbackFactory(CallbackData, prefix="user"):
    telegram_id: int
