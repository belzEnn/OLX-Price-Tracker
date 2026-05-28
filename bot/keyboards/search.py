from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def main_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Пошук")
    builder.button(text="Мої підписки")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def results_keyboard(query: str, next_offset: int, has_more: bool, subscribed: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if has_more:
        builder.button(text="Далі ➡️", callback_data=f"next:{query}:{next_offset}")

    if subscribed:
        builder.button(text="🔕 Скасувати підписку", callback_data=f"unsub:{query}")
    else:
        builder.button(text="🔔 Слідкувати", callback_data=f"sub:{query}")

    builder.adjust(1)
    return builder.as_markup()