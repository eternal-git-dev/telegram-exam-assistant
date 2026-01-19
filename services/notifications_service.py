import asyncio
from aiogram import exceptions
from aiogram import Bot
from core.config import settings

class NotificationsService:
    async def notify_admins(self, bot: Bot, text: str, admins=settings.ADMIN_IDS, reply_markup=None) -> None:
        tasks = [
            self._send_with_catch(bot, admin_id, text, reply_markup)
            for admin_id in admins
        ]
        await asyncio.gather(*tasks)

    async def send_to_admin_background(self, bot: Bot, admin_id: int, text: str, reply_markup=None):
        try:
            await bot.send_message(chat_id=admin_id, text=text, reply_markup=reply_markup)
        except Exception as exc:
            print(exc)

    async def _send_with_catch(self, bot: Bot, admin_id: int, text: str, reply_markup=None):
        try:
            await bot.send_message(chat_id=admin_id, text=text, reply_markup=reply_markup)
        except Exception as exc:
            print(exc)

    async def send_message_by_tg_id(self, bot: Bot, receiver_id: int, text: str, reply_markup=None):
        try:
            await bot.send_message(chat_id=receiver_id, text=text, reply_markup=reply_markup)
            return True
        except exceptions.ClientDecodeError:
            print(f"Не удалось отправить сообщение пользователю {receiver_id}: бот заблокирован")
            return False
        except exceptions.TelegramNotFound:
            print(f"Не удалось отправить сообщение пользователю {receiver_id}: чат или пользователь не найден")
            return False
        except exceptions.TelegramRetryAfter as e:
            print(
                f"Телеграм просит подождать {e.retry_after} секунд перед повторной отправкой сообщения пользователю {receiver_id}")
            return False
        except exceptions.TelegramAPIError:
            print(f"Не удалось отправить сообщение пользователю {receiver_id}: ошибка Telegram API")
            return False