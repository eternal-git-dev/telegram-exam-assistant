from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram import F, Router
from middlewares import BanMiddleWare
from keyboards.common_keyboards import get_global_keyboard
from utils import is_admin
from core.config import admin_commands
from services.orders_service import OrderService


user_router = Router()
user_router.message.middleware(BanMiddleWare())


@user_router.message(CommandStart())
async def start(message: Message):
    id_user = message.from_user.id
    check_adm = is_admin(id_user)
    if check_adm:
        commands = "\n".join([f"{command}" for command in admin_commands])
        return await message.answer(f'Список доступных команд администратора:\n{commands}')
    await message.answer(
        'Привет! Я — помощник по подготовке к экзаменам. Помогу записаться на консультации, отслеживать дедлайны и находить подходящие форматы занятий.',
        reply_markup=get_global_keyboard()
    )


@user_router.message(F.text == 'О нас')
async def about(message: Message):
    await message.answer(
        'ExamHelper — бот-помощник по подготовке к экзаменам. Вы можете записаться на консультацию, выбрать тему и формат занятия, а также просматривать свои заявки.'
    )


@user_router.message(F.text == 'Мои заявки')
async def my_orders(message: Message):
    id_user = message.from_user.id
    orders = await OrderService.get_user_orders(id_user)
    if orders is None:
        return await message.answer('Нет заявок для отображения!')
    orders_info = await OrderService.print_orders(orders=orders)
    text = '\n'.join([''.join(order) for order in orders_info])


    await message.answer(text)
