import asyncio
import logging

from aiogram import Bot, Dispatcher
from core.config import settings
from database.models import async_main
from handlers.admin import admin_router
from handlers.user import user_router
from handlers.order import order_router

bot = Bot(settings.BOT_TOKEN)


async def main():
    await async_main()
    dp = Dispatcher()
    dp.include_router(admin_router)
    dp.include_router(user_router)
    dp.include_router(order_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/bot_logs.log"),
            logging.StreamHandler()
        ],
        encoding="utf-8"
    )
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f'Critical error: {e}', exc_info=True)
