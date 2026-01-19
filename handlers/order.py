from datetime import datetime
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from core.config import Registration
from utils import parse_reply, check_deadline
from aiogram import F, Router

from keyboards.common_keyboards import get_global_keyboard
from keyboards.user_keyboards import get_subjects_by_university, university, type_works, reaction_keyboard


from middlewares import BanMiddleWare

from services.orders_service import OrderService
from services.notifications_service import NotificationsService


order_service = OrderService()
notify = NotificationsService()


order_router = Router()
order_router.message.middleware(BanMiddleWare())


@order_router.message(F.text == 'Записаться')
async def get_universities(message: Message, state: FSMContext):
    await state.set_state(Registration.user_id)
    user_id = int(message.from_user.id)
    await state.update_data(user_id=user_id)
    await state.set_state(Registration.university)
    universities_keyboard = await university()
    await message.answer('Выбери платформу/вуз, где ты готов заниматься:', reply_markup=universities_keyboard)


@order_router.callback_query(F.data.startswith('univers:'))
async def get_university_callback(callback: CallbackQuery, state: FSMContext):
    university_id = parse_reply(callback)
    if university_id is None:
        return callback.message.edit_text('Ошибка')
    university_id = int(university_id)
    await state.update_data(university=university_id)
    await state.set_state(Registration.subject)

    subjects_keyboard = await get_subjects_by_university(university_id)
    await callback.message.edit_text('Выбери предмет: ', reply_markup=subjects_keyboard)
    await callback.answer()


@order_router.callback_query(F.data.startswith('subject:'))
async def get_subject_callback(callback: CallbackQuery, state: FSMContext):
    subject_id = parse_reply(callback)
    if subject_id is None:
        return callback.message.edit_text('Ошибка предмета')
    subject_id = int(subject_id)
    await state.update_data(subject=subject_id)
    await state.set_state(Registration.type_work)
    type_keyboard = await type_works(subject_id)
    await callback.message.edit_text('Выберите тип занятия: ', reply_markup=type_keyboard)


@order_router.callback_query(F.data.startswith('type:'))
async def get_typework_callback(callback: CallbackQuery, state: FSMContext):
    type_id = parse_reply(callback)
    await state.update_data(type_work=type_id)
    await state.set_state(Registration.deadline)
    await callback.message.edit_text('Укажите к какому времени нужно выполнить твое задание. Формат ввода YY-MM-DD HH:MM, например: 1970-01-01 00:00\n'
                                     'Стандартное время выполнения от 3х до 7 дней, в зависимости от типа занятия.')


@order_router.message(Registration.deadline)
async def confirm_registration(message: Message, state: FSMContext):
    try:
        deadline = message.text
        data = await state.get_data()

        if not check_deadline(deadline):
            return await message.answer('Некорректный формат даты')

        deadline_datetime = datetime.strptime(deadline, "%Y-%m-%d %H:%M")

        order = await order_service.create_order({
            "user_id": data["user_id"],
            "university_id": data["university"],
            "subject_id": data["subject"],
            "type_work_id": data["type_work"],
            "deadline": deadline_datetime,
        })
        orders_info  = await order_service.print_orders(orders=[order])
        text = '\n'.join([''.join(order) for order in orders_info])
        await message.answer(text=f"Спасибо за заполнение формы" + text,
                             reply_markup=get_global_keyboard())

        admin_reply_markup = await reaction_keyboard(data["user_id"], order.id)

        await notify.notify_admins(
            bot=message.bot,
            text=text,
            reply_markup=admin_reply_markup
        )

    except ValueError:
        await message.answer("Некорректный дедлайн")
        return
    except LookupError:
        await message.answer("Пользователь не найден")
    except Exception as e:
        await message.answer("Ошибка получения пользователя. Попробуйте позже")
        print(f'Ошибка: {e}')

    await state.clear()