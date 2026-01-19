from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.admin_service import fetch_reference_data
from enums import OrderStatus, AdminDataType


async def add_university() -> InlineKeyboardMarkup:
    all_universities = await fetch_reference_data(AdminDataType.UNIVERSITIES)
    keyboard = InlineKeyboardBuilder()
    for uni in all_universities:
        keyboard.add(InlineKeyboardButton(
            text=uni.name,
            callback_data=f'add_univers:{uni.id}'
        ))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()


async def dell_university() -> InlineKeyboardMarkup:
    all_universities = await fetch_reference_data(AdminDataType.UNIVERSITIES)
    keyboard = InlineKeyboardBuilder()
    for uni in all_universities:
        keyboard.add(InlineKeyboardButton(
            text=uni.name,
            callback_data=f'dell_univers:{uni.id}'
        ))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()


async def add_subjects() -> InlineKeyboardMarkup:
    all_subjects = await fetch_reference_data(AdminDataType.SUBJECTS)
    keyboard = InlineKeyboardBuilder()
    for subject in all_subjects:
        keyboard.add(InlineKeyboardButton(
            text=subject.name,
            callback_data=f'add_subject:{subject.id}'
        ))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(4).as_markup()


async def dell_subjects() -> InlineKeyboardMarkup:
    all_subjects = await fetch_reference_data(AdminDataType.SUBJECTS)
    keyboard = InlineKeyboardBuilder()
    for subject in all_subjects:
        keyboard.add(InlineKeyboardButton(
            text=subject.name,
            callback_data=f'dell_subject:{subject.id}'
        ))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(4).as_markup()


async def type_works() -> InlineKeyboardMarkup:
    """Клавиатура для выбора типа заказа по статусу"""
    keyboard = InlineKeyboardBuilder()
    emoji_map = {
        OrderStatus.PENDING: "⏳",
        OrderStatus.COMPLETED: "✅",
        OrderStatus.CANCELLED: "❌",
    }

    for status in OrderStatus:
        keyboard.add(InlineKeyboardButton(
            text=f"{emoji_map.get(status, '⚪')} {status.value}",
            callback_data=f"view_data_type:{status.name}"
        ))

    keyboard.add(InlineKeyboardButton(text="⬅️ На главную", callback_data="to_main"))
    return keyboard.adjust(2).as_markup()


def get_data_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Платформы")],
            [KeyboardButton(text="Темы")],
            [KeyboardButton(text="Форматы")],
        ],
        resize_keyboard=True
    )