from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import settings
from loguru import logger

try:
    storage = MemoryStorage()
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher(storage=storage)
except Exception as e:
    logger.exception("An error occurred when initializing the bot")
    raise