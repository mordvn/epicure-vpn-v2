from pydantic_settings import BaseSettings
from typing import Optional
from loguru import logger
class Settings(BaseSettings):
    DEBUG: Optional[bool]
    TELEGRAM_BOT_TOKEN: str
    MARZBAN_SERVER_BASE_URL: str
    MARZBAN_SERVER_USERNAME: str
    MARZBAN_SERVER_PASSWORD: str
    PAYMENT_SUBSCRIBTION_PERIOD_DAYS: int
    @property
    def PAYMENT_SUBSCRIBTION_PERIOD_STR(self) -> int:
        return str(self.PAYMENT_SUBSCRIBTION_PERIOD_DAYS)
    SUBSCRIBTION_DATA_LIMIT_GB: int
    @property
    def SUBSCRIBTION_DATA_LIMIT_KB(self) -> int:
        return self.SUBSCRIBTION_DATA_LIMIT_GB * 1024 * 1024 * 1024
    PAYMENT_SUBSCRIBTION_PRICE_RUB: int
    YOO_KASSA_SHOP_ID: str
    YOO_KASSA_SECRET_KEY: str
    YOO_KASSA_RETURN_URL: str
    MONGODB_URL: str
    REFERRAL_BONUS_RUB: int
    REFERRAL_BONUS_PERCENT: int
    class Config:
        env_file = '.env'

try:
    settings = Settings()
    logger.info(f"Configuration file loaded")
except Exception as e:
    logger.exception("An error occurred when loading the configuration file")
    raise
