from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from enums import AdminDataType
from services.admin_service import fetch_reference_data
from services.reference_service import get_subjects_by_university_id, get_typeworks_for_subject


async def university() -> InlineKeyboardMarkup:
    all_universities = await fetch_reference_data(AdminDataType.UNIVERSITIES)
    keyboard = InlineKeyboardBuilder()
    for univer in all_universities:
        keyboard.add(InlineKeyboardButton(
            text=univer.name,
            callback_data=f'univers:{univer.id}'
        ))
    # Добавляем кнопку "На главную"
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()  # Возвращаем сразу готовый markup


async def subjects() -> InlineKeyboardMarkup:
    all_subjects = await fetch_reference_data(AdminDataType.SUBJECTS)
    keyboard = InlineKeyboardBuilder()
    for subject in all_subjects:
        keyboard.add(InlineKeyboardButton(
            text=subject.name,
            callback_data=f'subject:{subject.id}'
        ))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(4).as_markup()


async def type_works(subject_id: int) -> InlineKeyboardMarkup:
    all_types = await get_typeworks_for_subject(subject_id)
    keyboard = InlineKeyboardBuilder()
    if all_types:
        for t in all_types:
            keyboard.add(InlineKeyboardButton(
                text=t.name,
                callback_data=f'type:{t.id}'
            ))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()


async def get_subjects_by_university(university_id: int) -> InlineKeyboardMarkup:
    all_subjects = await get_subjects_by_university_id(university_id)
    keyboard = InlineKeyboardBuilder()
    if all_subjects:
        for subject in all_subjects:
            keyboard.add(InlineKeyboardButton(
                text=subject.name,
                callback_data=f'subject:{subject.id}'
            ))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(4).as_markup()


async def reaction_keyboard(user_id: int, id_order: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text='Контакт', callback_data=f'contact:{user_id}'),
        InlineKeyboardButton(text='Отменить заявку', callback_data=f'cancel_order:{id_order}'),
        InlineKeyboardButton(text='Завершить заявку', callback_data=f'accept_order:{id_order}')
    )
    return keyboard.adjust(1).as_markup()
