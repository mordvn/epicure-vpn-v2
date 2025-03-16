from beanie import Document
from typing import Optional

class Referral(Document):
    user_id: int
    referrer_id: int

    class Settings:
        name = "referrals"
        indexes = [
            "user_id",  # Index for faster lookups
        ] 