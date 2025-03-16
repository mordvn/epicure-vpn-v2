from loguru import logger
import sys
import asyncio
from bot import dp, bot
from services.include_services import include_services
from routers.include_routers import include_routers

from config import settings
logger.warning(f"DEBUG flag expected: {settings.DEBUG}")

if settings.DEBUG:
    logger.remove()
    logger.add(sys.stdout, level="TRACE")

async def main():
    try:
        logger.debug("Including services...")
        await include_services(dp)
        logger.info("Services included")   

        logger.debug("Including routers...")
        await include_routers(dp)
        logger.info("Routers included")

        logger.info("Starting polling...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception("An error occurred when starting the bot")
        raise

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception("An error occurred when running the bot")
        raise
