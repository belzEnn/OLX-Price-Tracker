from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def main_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Пошук")
    return builder.as_markup(resize_keyboard=True)


def next_keyboard(query: str, next_offset: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Далі", callback_data=f"next:{query}:{next_offset}")
    return builder.as_markup()