from datetime import datetime
from loguru import logger
from typing import List, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from models.transaction import Transaction
from beanie import init_beanie

class Balance:
    def __init__(self, mongodb_url: str, database_name: str = "epicurevpn"):
        self.currency = "CRYSTALS"
        self.client = AsyncIOMotorClient(mongodb_url)
        self.database = self.client[database_name]
        
    async def init(self):
        """Initialize database connection and Beanie models"""
        try:
            # Initialize Beanie with the database
            await init_beanie(
                database=self.database,
                document_models=[Transaction]
            )
            logger.trace(f"Balance service initialized with MongoDB database: {self.database.name}")
        except Exception as e:
            logger.error(f"Failed to initialize Balance service: {e}")
            raise

    async def register_income(self, user_id: int, value: float, note: str) -> bool:
        try:
            transaction = Transaction(
                user_id=user_id,
                type="income",
                value=value,
                note=note,
                timestamp=datetime.now()
            )
            await transaction.insert()
            return True
        except Exception as e:
            logger.error(f"Error registering income for user {user_id}: {e}")
            return False

    async def register_expense(self, user_id: int, value: float, note: str) -> bool:
        """
        Register expense transaction
        Returns True if transaction was registered successfully
        """
        try:
            transaction = Transaction(
                user_id=user_id,
                type="expense", 
                value=-abs(value),
                note=note,
                timestamp=datetime.now()
            )
            await transaction.insert()
            return True
        except Exception as e:
            logger.error(f"Error registering expense for user {user_id}: {e}")
            return False

    def get_currency(self) -> str:
        """
        Get current currency
        """
        return self.currency

    async def get_history(self, user_id: int, limit: Optional[int] = None) -> List[Dict]:
        """
        Get transaction history for a specific user
        Optional limit parameter to restrict number of transactions returned
        """
        try:
            query = Transaction.find({"user_id": user_id}).sort(-Transaction.timestamp)
            if limit:
                query = query.limit(limit)
            transactions = await query.to_list()
            return [t.dict() for t in transactions]
        except Exception as e:
            logger.error(f"Error getting transaction history for user {user_id}: {e}")
            return []

    async def get_balance(self, user_id: int) -> float:
        """
        Get balance by user ID
        """
        try:
            transactions = await Transaction.find({"user_id": user_id}).to_list()
            balance = sum(t.value for t in transactions)
            return balance
        except Exception as e:
            logger.error(f"Error getting balance for user {user_id}: {e}")
            return 0.0

    async def enough_balance(self, user_id: int, amount: float) -> bool:
        """
        Check if user has enough balance for a transaction
        """
        balance = await self.get_balance(user_id)
        return balance >= amount
