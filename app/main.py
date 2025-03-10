import asyncio
import logging
import sys
from config import settings
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from routers.include_routers import include_routers
from services.include_services import include_services

logger = logging.getLogger(__name__)

if settings.DEBUG:
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format='%(asctime)s - %(name)s - %(filename)s - %(levelname)s - %(message)s'
    )
else:
    logging.basicConfig(
        level=logging.WARNING,
        stream=sys.stdout,
        format='%(asctime)s - %(name)s - %(filename)s - %(levelname)s - %(message)s'
    )



bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

async def main():
    include_services(dp)
    include_routers(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass