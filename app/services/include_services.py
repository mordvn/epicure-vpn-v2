from services.marzban import Marzban
from services.yookassa import Yookassa
from services.balance import Balance
from services.referral import ReferralSystem
from config import settings

async def include_services(dp):
    # Initialize services with MongoDB URL and database name
    dp['marzban'] = Marzban()
    dp['yookassa'] = Yookassa()

    balance_service = Balance(settings.MONGODB_URL)
    await balance_service.init()

    referral_service = ReferralSystem(settings.MONGODB_URL)
    await referral_service.init()
    dp['balance'] = balance_service
    dp['referral'] = referral_service