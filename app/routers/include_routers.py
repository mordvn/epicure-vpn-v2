from loguru import logger
from aiogram import Dispatcher
from aiogram_dialog import Dialog
from routers.start import router as start_router
from routers.windows.subscription_window import subscription_window
from routers.windows.payment_window import payment_window
from routers.windows.in_payment_window import in_payment_window
from routers.windows.referral_system_window import referral_system_window
from aiogram_dialog import setup_dialogs

dialog = Dialog(
    subscription_window,
    payment_window,
    in_payment_window,
    referral_system_window,
)

async def include_routers(dp: Dispatcher):
    try:
        dp.include_router(start_router)
        dp.include_router(dialog)
        setup_dialogs(dp)
    except Exception as e:
        logger.exception("An error occurred when including routers")
        raise