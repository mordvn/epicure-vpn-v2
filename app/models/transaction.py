from datetime import datetime
from beanie import Document
from typing import Literal

class Transaction(Document):
    user_id: int
    type: Literal["income", "expense"]
    value: float
    note: str
    timestamp: datetime = datetime.now()

    class Settings:
        name = "transactions"
        indexes = [
            "user_id",  # Index for faster lookups by user
        ] 