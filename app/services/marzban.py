from marzban import MarzbanAPI
from datetime import datetime, timedelta
from config import settings

from marzban import MarzbanAPI, AdminCreate, UserCreate, NodeCreate, UserTemplateCreate, AdminModify, UserModify, \
    UserTemplateModify, NodeModify, ProxySettings, MarzbanTokenCache


class Marzban:
    """https://github.com/sm1ky/marzban_api/blob/production/example/example.py
    https://connect.epicure-network.space/docs#/User/get_users_usage"""
    def __init__(self):
        self.api = MarzbanAPI(base_url=settings.MARZBAN_SERVER_BASE_URL)
        self.token_cache = MarzbanTokenCache(
            client=self.api,
            username=settings.MARZBAN_SERVER_USERNAME,
            password=settings.MARZBAN_SERVER_PASSWORD
        )

    async def get_token(self):
        """Get access token for Marzban API"""
        return await self.token_cache.get_token()

    async def get_user(self, username: str):
        """Get user information"""
        token = await self.get_token()
        return await self.api.get_user(username=username, token=token)

    async def create_user(self, username: str, expire: int, data_limit: int):
        """Add a new user"""
        token = await self.get_token()

        new_user = UserCreate(username=username, proxies={"vless": ProxySettings(flow="xtls-rprx-vision")},
                          inbounds={'vless': ['VLESS TCP REALITY']}, expire=expire, data_limit=data_limit)
        return await self.api.add_user(user=new_user, token=token)

    async def update_user(self, username: str, expire: int, data_limit: int):
        """Modify user details"""
        token = await self.get_token()
        return await self.api.modify_user(username=str(username), user=UserModify(expire=expire, data_limit=data_limit, status="active"), token=token)

    async def user_active(self, user_telegram_id: int) -> bool:
        try:
            marz_user = await self.get_user(user_telegram_id)
            return marz_user.status == "active"
        except Exception:
            return False