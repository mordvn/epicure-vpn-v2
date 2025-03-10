from pydantic_settings import BaseSettings
from typing import Optional
class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    DEBUG: Optional[bool]
    MARZBAN_SERVER_BASE_URL: str
    MARZBAN_SERVER_USERNAME: str
    MARZBAN_SERVER_PASSWORD: str
    PAYMENT_SUBSCRIBTION_PERIOD_STR: str
    PAYMENT_SUBSCRIBTION_PERIOD_DAYS: int
    SUBSCRIBTION_DATA_LIMIT_KB: int
    SUBSCRIBTION_DATA_LIMIT_GB: int
    PAYMENT_SUBSCRIBTION_PRICE_RUB: int
    PAYMENT_SUCCESS_PAY_MESSAGE_EFFECT: str
    YOO_KASSA_SHOP_ID: int
    YOO_KASSA_SECRET_KEY: str
    YOO_KASSA_RETURN_URL: str
    SUBSCRIBTION_PERIOD_DAYS: int

    class Config:
        env_file = '.env'

settings = Settings()