from database.requests import (
    get_user_by_tg, ban_user,
    unban_user, is_banned,
    user_exists)
from database.models import async_session
from enums import OperationResult

from cache.redis_cache import cached


async def user_info(tg_id: int):
    async with async_session() as session:
        op_result, user = await get_user_by_tg(session=session, user_id=tg_id)

        if op_result is not OperationResult.SUCCESS:
            return None
        return {"id": user.tg_id, "nickname": user.nickname, "fullname": user.fullname, "banned": user.banned}

@cached(key_builder=lambda user_id: str(user_id), ttl=15)
async def user_banned(user_tg_id: int) -> bool:
    async with async_session() as session:
        op, user = await get_user_by_tg(session=session, user_id=user_tg_id)
        if op != OperationResult.SUCCESS:
            return False
        return bool(user and user.banned)


async def ban_user_service(user_tg_id):

    if await user_banned(user_tg_id):
        return OperationResult.SUCCESS

    async with async_session() as session:
        op_result, user = await get_user_by_tg(session=session, user_id=user_tg_id)

        if op_result is not OperationResult.SUCCESS:
            return OperationResult.NOT_FOUND

        if user.banned:
            return OperationResult.SUCCESS

        op_result, status = await ban_user(session, user_tg_id)
        if status:
            await session.commit()
            return OperationResult.SUCCESS
        else:
            await session.rollback()
            return op_result


async def unban_user_service(user_tg_id):
    async with async_session() as session:
        op_result, user = await get_user_by_tg(session=session, user_id=user_tg_id)
        if op_result is not OperationResult.SUCCESS:
            return OperationResult.NOT_FOUND

        if not user.banned:
            return OperationResult.SUCCESS

        op_result, status = await unban_user(session, user_tg_id)
        if op_result is OperationResult.SUCCESS:
            await session.commit()
            return op_result
        else:
            await session.rollback()
            return op_result
