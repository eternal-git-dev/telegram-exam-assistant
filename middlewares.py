from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
from utils import is_admin
from services.user_service import user_banned


class BanMiddleWare(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        id_user = event.from_user.id

        banned = await user_banned(id_user)
        if banned:
            return await event.answer('Вы забанены')

        return await handler(event, data)


class AdminMiddleWare(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        id_user = event.from_user.id
        if is_admin(id_user):
            return await handler(event, data)
        await event.answer("Эта команда доступна только администраторам")