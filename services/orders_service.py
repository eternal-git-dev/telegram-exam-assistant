from datetime import datetime
from typing import List

from aiogram.utils.markdown import hitalic

from sqlalchemy.exc import SQLAlchemyError

from database.models import Order, async_session
from database.requests import (
    create_order, get_user_by_tg,
    get_university_by_id, get_subject_by_id,
    get_type_work_by_id, set_order_status,
    get_orders_by_filters, get_orders_with_details)
from utils import parse_reply
from enums import OperationResult, OrderStatus
from core.config import order_available_status
import asyncio


class OrderService:
    @staticmethod
    async def create_order(data: dict) -> Order | None:

        async with async_session() as session:
            user_result = await get_user_by_tg(session, data["user_id"])
            if user_result[0] == OperationResult.NOT_FOUND:
                raise LookupError("Пользователь не найден")

            if user_result[0] == OperationResult.UNKNOWN_ERROR:
                raise Exception("Ошибка получения пользователя")

            order = await create_order(
                session,
                user_id=user_result[1].id,
                university_id=data["university_id"],
                subject_id=data["subject_id"],
                type_work_id=data["type_work_id"],
                deadline=data["deadline"],
            )

            await session.commit()
            await session.refresh(order)
            return order

    @staticmethod
    async def get_user_orders(user_id: int):
        try:
            async with async_session() as session:
                op_result, orders = await get_orders_by_filters(session=session, tg_id=user_id)

                if op_result != OperationResult.SUCCESS:
                    return None
                return orders
        except SQLAlchemyError:
            return None

    @staticmethod
    async def get_orders(**filters) -> list[Order] | None:
        """
        Универсальный метод для получения заказов по фильтрам

        Примеры использования:
        - await OrderService.get_orders(user_id=123)
        - await OrderService.get_orders(order_type=OrderStatus.ACTIVE, subject_id=5)
        - await OrderService.get_orders(status=OrderStatus.COMPLETED, university_id=1)
        """
        try:
            async with async_session() as session:
                if not filters:
                    op_result, orders = await get_orders_by_filters(session=session)
                else:
                    op_result, orders = await get_orders_by_filters(session=session, **filters)

                if op_result != OperationResult.SUCCESS:
                    return None
                return orders
        except SQLAlchemyError:
            return None


    @staticmethod
    async def print_orders(orders: list[Order]) -> list:
        result = []
        async with async_session() as session:
            for order in orders:
                university_result, subject_result, type_work_result = await asyncio.gather(
                    get_university_by_id(session, order.id_university),
                    get_subject_by_id(session, order.id_subject),
                    get_type_work_by_id(session, order.id_type_work)
                )

                if all([
                    university_result[0] == OperationResult.SUCCESS,
                    subject_result[0] == OperationResult.SUCCESS,
                    type_work_result[0] == OperationResult.SUCCESS
                ]):
                    result.append(
                        f'id заявки: {order.id}\n'
                        f'Платформа: {university_result[1].name}\n'
                        f'Тема: {subject_result[1].name}\n'
                        f'Формат занятия: {type_work_result[1].name}\n'
                        f'Дедлайн: {order.deadline}'
                    )
                else:
                    result.append(
                        f'id заявки: {order.id}\n'
                        f'Ошибка загрузки данных заявки'
                    )
        return result

    @staticmethod
    async def set_status(order_id, status: OrderStatus):
        if status not in order_available_status:
            return OperationResult.NOT_FOUND
        try:
            async with async_session() as session:
                op_result = await set_order_status(session=session, order_id=order_id, status=status.name)
                if not op_result:
                    return False
                await session.commit()
                return order_id
        except SQLAlchemyError as e:
            print(f'{e}')
            return False

    @staticmethod
    async def cancel_order_by_id(callback):
        order_id = parse_reply(callback)
        return await OrderService.set_status(order_id, OrderStatus.CANCELLED)

    @staticmethod
    async def complete_order_by_id(callback):
        order_id = parse_reply(callback)
        return await OrderService.set_status(order_id, OrderStatus.COMPLETED)

    @staticmethod
    async def get_orders_by_user(user_id: int) -> list[Order] | None:
        return await OrderService.get_orders(user_id=user_id)

    @staticmethod
    async def get_orders_by_status(status: OrderStatus) -> list[Order] | None:
        return await OrderService.get_orders(status=status)

    @staticmethod
    async def get_orders_by_type(type_work_id: int) -> list[Order] | None:
        return await OrderService.get_orders(type_work_id=type_work_id)

    @staticmethod
    async def get_orders_by_subject(subject_id: int) -> list[Order] | None:
        return await OrderService.get_orders(subject_id=subject_id)

    @staticmethod
    async def get_active_orders() -> list[Order] | None:
        return await OrderService.get_orders(status=OrderStatus.PENDING)

    @staticmethod
    async def get_orders_for_display(**filters) -> List[Order] | None:
        try:
            async with async_session() as session:
                op_result, orders = await get_orders_with_details(
                    session=session,
                    **filters
                )
                if op_result != OperationResult.SUCCESS:
                    return None
                return orders
        except SQLAlchemyError:
            return None

    @staticmethod
    def format_order(order: Order) -> str:
        try:
            # Базовые данные
            text = f"{'📋 Заказ'} #{order.id}\n\n"

            # Статус с эмодзи
            status_emoji = {
                "completed": "🟢",
                "cancelled": "🔴",
                "pending": "⏳"
            }
            status = order.status.value if order.status else "unknown"
            text += f"{status_emoji.get(status, '⚪')} {'Статус:'} {status}\n"

            # Пользователь
            if order.user:
                text += f"👤 {'Пользователь:'} {order.user.nickname or f'ID: {order.user.id}'}\n"

            # Основные данные
            if order.university:
                text += f"🎓 {'ВУЗ:'} {order.university.name}\n"

            if order.subject:
                text += f"📚 {'Предмет:'} {order.subject.name}\n"

            if order.type_work:
                text += f"📝 {'Тип работы:'} {order.type_work.name}\n"

            # Дедлайн
            if order.deadline:
                deadline_str = order.deadline.strftime("%d.%m.%Y %H:%M")
                now = datetime.now()
                if order.deadline < now:
                    text += f"⏰ {'Дедлайн:'} ⌛ Просрочено ({deadline_str})\n"
                else:
                    days_left = (order.deadline - now).days
                    text += f"⏰ {'Дедлайн:'} {deadline_str} ({days_left} дн.)\n"

            return text

        except Exception as e:
            return f"Ошибка форматирования заказа #{order.id}: {str(e)}"

    @staticmethod
    def format_orders_list(orders: List[Order], page: int = 1, per_page: int = 10) -> List[str]:
        """Форматирование списка заказов с пагинацией"""
        if not orders:
            return ["Заказы не найдены"]

        # Пагинация
        total_orders = len(orders)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_orders = orders[start_idx:end_idx]

        formatted = []

        # Заголовок с информацией о странице
        header = f"{'📊 Список заказов'}\n"
        header += f"Страница {page} из {((total_orders - 1) // per_page) + 1}\n"
        header += f"Всего заказов: {total_orders}\n"
        formatted.append(header)

        # Форматирование заказов на странице
        for i, order in enumerate(page_orders, start=start_idx + 1):
            order_text = OrderService.format_order(order)
            formatted.append(order_text)

        # Если есть еще страницы
        if end_idx < total_orders:
            formatted.append(f"\n{hitalic('Используйте /orders [номер страницы] для перехода к следующей странице')}")

        return formatted
