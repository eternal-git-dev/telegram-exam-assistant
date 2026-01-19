from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def get_global_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.add(
        KeyboardButton(text="Мои заявки"),
        KeyboardButton(text="О нас"),
        KeyboardButton(text="Записаться"),
    )

    builder.adjust(1)  # по одной кнопке в строке
    return builder.as_markup(resize_keyboard=True)