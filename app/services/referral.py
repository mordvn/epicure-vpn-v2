from loguru import logger
from aiogram.utils.deep_linking import create_start_link
from aiogram import Bot
from config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from models.referral import Referral
from beanie import init_beanie
from typing import Optional

class ReferralSystem:
    def __init__(self, mongodb_url: str, database_name: str = "epicurevpn"):
        self.client = AsyncIOMotorClient(mongodb_url)
        self.database = self.client[database_name]

    async def init(self):
        try:
            await init_beanie(
                database=self.database,
                document_models=[Referral]
            )
            logger.trace(f"ReferralSystem service initialized with MongoDB database: {self.database.name}")
        except Exception as e:
            logger.error(f"Failed to initialize ReferralSystem service: {e}")
            raise

    async def get_referral_link(self, bot: Bot, user_id: int) -> str:
        try:
            logger.debug("Referrer link created")
            return await create_start_link(bot, user_id, encode=True)
        except Exception as e:
            logger.error(f"Error generating referral link: {e}")
            return None

    async def set_referrer(self, user_id: int, referrer_id: int = None) -> bool:
        try:
            if not referrer_id or user_id == referrer_id:
                return False

            # Check if user already has a referrer
            existing_referral = await Referral.find_one({"user_id": user_id})
            if existing_referral:
                return False

            # Save referrer to database
            referral = Referral(user_id=user_id, referrer_id=referrer_id)
            await referral.insert()

            logger.debug("Referrer registered")
            return True

        except Exception as e:
            logger.error(f"Error setting referrer: {e}")
            return False

    async def get_referrer(self, user_id: int) -> Optional[int]:
        try:
            referral = await Referral.find_one({"user_id": user_id})
            if referral:
                return referral.referrer_id
            return None
        except Exception as e:
            logger.error(f"Error getting referrer for user {user_id}: {e}")
            return None
