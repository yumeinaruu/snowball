from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def generate_prev_stop_next_keyboard(prev: bool = True, stop: bool = True, next: bool = True):
    prev_btn = InlineKeyboardButton(text="<<<", callback_data="valentinmessages_prev")
    stop_btn = InlineKeyboardButton(text="O", callback_data="valentinmessages_end")
    next_btn = InlineKeyboardButton(text=">>>", callback_data="valentinmessages_next")
    buttons = []

    if prev:
        buttons.append(prev_btn)
    if stop:
        buttons.append(stop_btn)
    if next:
        buttons.append(next_btn)
    builder = InlineKeyboardBuilder()
    builder.row(*buttons)
    return builder
