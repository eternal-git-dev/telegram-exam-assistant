from datetime import datetime

from database.models import OrderStatus
from database.models import User, University, TypeWork, Subject, Order, subject_typework_association
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, exists, and_
from cache.redis_cache import cached
from enums import OperationResult
from sqlalchemy.ext.asyncio import AsyncSession


async def set_user(session: AsyncSession, tg_id, username, fullname):
    try:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            new_user = User(tg_id=tg_id, nickname=username, fullname=fullname)
            session.add(new_user)
            await session.flush()
    except SQLAlchemyError as e:
        await session.rollback()
        print(e)


async def set_concat_data(session: AsyncSession, tg_id, username, fullname):
    try:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            user.fullname = fullname
            user.nickname = username
            await session.flush()
    except SQLAlchemyError as e:
        await session.rollback()
        print(e)


async def is_banned(session, user_id) -> bool:
    try:
        user = await session.scalar(select(User).where(User.tg_id == user_id))
        return bool(user and user.banned)
    except SQLAlchemyError as e:
        print(e)
        return False


async def get_user_by_tg(session, user_id):
    try:
        user = await session.scalar(select(User).where(User.tg_id == user_id))
        if user:
            return OperationResult.SUCCESS, user
        else:
            return OperationResult.NOT_FOUND, None
    except SQLAlchemyError as e:
        print(f"Ошибка получения пользователя {user_id}: {e}")
        return OperationResult.UNKNOWN_ERROR, None


async def user_exists(session: AsyncSession, user_id: int) -> bool:
    user = await session.scalar(select(User).where(User.tg_id == user_id))
    return bool(user)

async def get_subject(session: AsyncSession, university_id):
    try:
        subjects = await session.scalars(select(Subject).where(Subject.university_id == university_id))
        if subjects:
            return OperationResult.SUCCESS, subjects.all()
        else:
            return OperationResult.NOT_FOUND, None
    except SQLAlchemyError as e:
        print(f"Ошибка получения {university_id}: {e}")
        return OperationResult.UNKNOWN_ERROR, None


async def get_universities(session):
    try:
        universities = await session.scalars(select(University))
        return universities.all() if universities else OperationResult.NOT_FOUND
    except SQLAlchemyError as e:
        print(f'{e}')
        return OperationResult.UNKNOWN_ERROR


async def get_subjects(session):
    try:
        subjects = await session.scalars(select(Subject))
        return subjects.all() if subjects else OperationResult.NOT_FOUND
    except SQLAlchemyError as e:
        print(f'{e}')
        return OperationResult.UNKNOWN_ERROR


async def get_typeworks(session):
    try:
        typeworks = await session.scalars(select(TypeWork))
        return typeworks.all() if typeworks else OperationResult.NOT_FOUND
    except SQLAlchemyError as e:
        print(f'{e}')
        return OperationResult.UNKNOWN_ERROR


async def get_typework(session: AsyncSession, typework_name: str):
    try:
        typework = await session.scalar(select(TypeWork).where(TypeWork.name == typework_name))
        if typework is None:
            return OperationResult.NOT_FOUND, None
        return OperationResult.SUCCESS, typework
    except Exception as e:
        print(e)
        return OperationResult.UNKNOWN_ERROR, None


async def create_order(
    session,
    user_id: int,
    university_id: int,
    subject_id: int,
    type_work_id: int,
    deadline: datetime
) -> Order | OperationResult:
    try:
        order = Order(
            id_user=user_id,
            id_university=university_id,
            id_subject=subject_id,
            id_type_work=type_work_id,
            deadline=deadline,
            status=OrderStatus.PENDING,
        )
        session.add(order)
        await session.flush()
        return order
    except SQLAlchemyError as e:
        print(f'Ошибка в ордере {e}')
        await session.rollback()
        return OperationResult.UNKNOWN_ERROR


async def get_orders_with_details(
    session,
    **filters
) -> tuple[OperationResult, list[Order] | None]:
    try:
        query = select(Order).options(
            selectinload(Order.university),
            selectinload(Order.subject),
            selectinload(Order.type_work),
            selectinload(Order.user)
        )

        for field, value in filters.items():
            if hasattr(Order, field) and value is not None:
                query = query.where(getattr(Order, field) == value)

        result = await session.execute(query)
        orders = result.scalars().all()

        if orders:
            return OperationResult.SUCCESS, orders
        else:
            return OperationResult.NOT_FOUND, None

    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return OperationResult.UNKNOWN_ERROR, None

async def get_orders_by_filters(
        session,
        **filters
):
    """
    Универсальная функция для получения заказов по фильтрам
    """
    try:
        query = select(Order)

        # Применяем фильтры
        for field, value in filters.items():
            if hasattr(Order, field) and value is not None:
                query = query.where(getattr(Order, field) == value)

        result = await session.execute(query)
        orders = result.scalars().all()

        if orders:
            return OperationResult.SUCCESS, orders
        else:
            return OperationResult.NOT_FOUND, None

    except SQLAlchemyError as e:
        print(f"Database error in get_orders_by_filters: {e}")
        return OperationResult.UNKNOWN_ERROR, None


async def get_university_by_id(session, university_id):
    try:
        result = await session.scalar(select(University).where(University.id == university_id))
        if result:
            return OperationResult.SUCCESS, result
        else:
            return OperationResult.NOT_FOUND, None
    except SQLAlchemyError as e:
        print(f'{e}')
        return OperationResult.UNKNOWN_ERROR, None


async def get_type_work_by_id(session, type_work_id):
    try:
        result = await session.scalar(select(TypeWork).where(TypeWork.id == type_work_id))
        if result:
            return OperationResult.SUCCESS, result
        else:
            return OperationResult.NOT_FOUND, None
    except SQLAlchemyError as e:
        print(f'{e}')
        return OperationResult.UNKNOWN_ERROR, None


async def get_subject_by_id(session, subject_id):
    try:
        result = await session.scalar(select(Subject).where(Subject.id == subject_id))
        if result:
            return OperationResult.SUCCESS, result
        else:
            return OperationResult.NOT_FOUND, None
    except SQLAlchemyError as e:
        print(f'{e}')
        return OperationResult.UNKNOWN_ERROR, None


async def ban_user(session, id_user):
    try:
        result = await session.scalar(select(User).where(User.tg_id == id_user))
        if result:
            result.banned = True
            await session.flush()
            return OperationResult.SUCCESS, True
        return OperationResult.NOT_FOUND, False
    except SQLAlchemyError as e:
        print(f'{e}')
        await session.rollback()
        return OperationResult.UNKNOWN_ERROR, False


async def unban_user(session, id_user):
    try:
        result = await session.scalar(select(User).where(User.tg_id == id_user))
        if result:
            result.banned = False
            await session.flush()
            return OperationResult.SUCCESS, True

        return OperationResult.NOT_FOUND, False
    except SQLAlchemyError as e:
        await session.rollback()
        print(f'{e}')
        return OperationResult.UNKNOWN_ERROR, False


async def set_order_status(session, order_id, status):
    try:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        if not order:
            return OperationResult.FAILED
        order.status = status
        await session.flush()
        return OperationResult.SUCCESS
    except SQLAlchemyError as e:
        await session.rollback()
        print(f"{e}")
        return OperationResult.UNKNOWN_ERROR


async def dell_subject(session, subject_name: str, university_id: int):
    try:
        subject = await session.scalar(select(Subject).where(and_(Subject.name == subject_name, Subject.university_id == university_id)))
        if subject is None:
            return OperationResult.NOT_FOUND
        await session.delete(subject)
        await session.flush()
        return OperationResult.SUCCESS
    except SQLAlchemyError as e:
        await session.rollback()
        print(f"{e}")
        return OperationResult.UNKNOWN_ERROR


async def add_subject(session, subject_name, university_id):
    try:
        subject = await session.scalar(select(Subject).where(and_(Subject.name == subject_name, Subject.university_id == university_id)))
        university = await session.scalar(select(University).where(University.id == university_id))
        if university is None:
            return OperationResult.NOT_FOUND
        if subject is not None:
            return OperationResult.EXISTS
        new_subject = Subject(name=subject_name, university_id=university_id)
        session.add(new_subject)
        await session.flush()
        return OperationResult.SUCCESS
    except SQLAlchemyError as e:
        await session.rollback()
        print(f"{e}")
        return OperationResult.UNKNOWN_ERROR


async def add_type(session, typework_name: str, subject_id: int):
    try:
        type_work = await session.scalar(
            select(TypeWork).where(TypeWork.name == typework_name)
        )

        if type_work is None:
            type_work = TypeWork(name=typework_name)
            session.add(type_work)
            await session.flush()
        else:
            association_exists = await session.scalar(
                select(
                    exists().where(
                        and_(
                            subject_typework_association.c.subject_id == subject_id,
                            subject_typework_association.c.typework_id == type_work.id
                        )
                    )
                )
            )

            if association_exists:
                return OperationResult.EXISTS

        stmt = subject_typework_association.insert().values(
            subject_id=subject_id,
            typework_id=type_work.id
        )
        await session.execute(stmt)
        return OperationResult.SUCCESS

    except Exception as e:
        await session.rollback()
        print(f"Error: {e}")
        return OperationResult.FAILED


async def get_subject_with_typeworks(session: AsyncSession, subject_id: int):
    try:

        stmt = select(Subject).where(Subject.id == subject_id).options(selectinload(Subject.typeworks))
        result = await session.execute(stmt)
        subject = result.scalar_one_or_none()
        if subject:
            return OperationResult.SUCCESS, subject.typeworks
        else:
            return OperationResult.NOT_FOUND, None
    except SQLAlchemyError as e:
        print(f"{e}")
        return OperationResult.UNKNOWN_ERROR, None


async def get_universities_by_subject(session: AsyncSession, subject_name):
    try:
        universities = await session.scalars(select(Subject.university_id).where(Subject.name == subject_name))
        if universities:
            return OperationResult.SUCCESS, universities.all()
        else:
            return OperationResult.NOT_FOUND, None
    except SQLAlchemyError as e:
        print(f"{e}")
        return OperationResult.UNKNOWN_ERROR, None


async def remove_association(session, subject_id: int, typework_id: int):
    try:
        subject = await session.scalar(select(Subject).where(Subject.id == subject_id))
        if not subject:
            return OperationResult.NOT_FOUND, None

        typework = await session.scalar(select(TypeWork).where(TypeWork.id == typework_id))

        if not typework:
            return OperationResult.NOT_FOUND, None

        if typework not in subject.typeworks:
            return OperationResult.FAILED, None

        subject.typeworks.remove(typework)
        await session.flush()
        return OperationResult.SUCCESS, True
    except SQLAlchemyError as e:
        print(f"{e}")
        await session.rollback()
        return OperationResult.UNKNOWN_ERROR, None