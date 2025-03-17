from aiogram_dialog import Window, DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Back
from aiogram.types import CallbackQuery
from datetime import datetime, timedelta
from services.balance import Balance
from states import BotStates
from services.yookassa import Yookassa
from services.marzban import Marzban
from services.referral import ReferralSystem
from services.balance import Balance

from config import settings
from loguru import logger
import asyncio

CHECK_PAYMENT_TIMEOUT_MINUTES = 10

async def _register_success_payment(manager: DialogManager, user_telegram_id: int, months: int, marzban: Marzban, referrer_id: int, balance: Balance):
    if await marzban.user_active(user_telegram_id):
        marz_user = await marzban.get_user(user_telegram_id)
        new_sub_finish_time = int((datetime.fromtimestamp(marz_user.expire) + timedelta(days=settings.PAYMENT_SUBSCRIBTION_PERIOD_DAYS*months)).timestamp())
        await marzban.update_user(str(user_telegram_id), new_sub_finish_time, settings.SUBSCRIBTION_DATA_LIMIT_KB)
        await manager.switch_to(BotStates.subscription_view)
    else:
        new_sub_finish_time = int((datetime.now() + timedelta(days=settings.PAYMENT_SUBSCRIBTION_PERIOD_DAYS*months)).timestamp())
        await marzban.create_user(str(user_telegram_id), new_sub_finish_time, settings.SUBSCRIBTION_DATA_LIMIT_KB)
        await manager.switch_to(BotStates.subscription_view)
    logger.trace(f"Payment success: {user_telegram_id} {months}")

    if referrer_id:
        await balance.register_income(
            user_id=referrer_id, 
            value=settings.REFERRAL_BONUS_RUB, 
            note=f"Реферальный бонус от {user_telegram_id}"
        )
        logger.trace(f"Referrer bonus registered: {referrer_id} {user_telegram_id}")

async def _check_payment(manager: DialogManager):
    user_telegram_id = manager.event.from_user.id

    payment_id = manager.dialog_data.get("payment_id")
    months = manager.dialog_data.get("months")

    yookassa: Yookassa = manager.middleware_data.get("yookassa")
    marzban: Marzban = manager.middleware_data.get("marzban")
    referral: ReferralSystem = manager.middleware_data.get("referral")
    balance: Balance = manager.middleware_data.get("balance")
    
    referrer_id = await referral.get_referrer(user_telegram_id)

    manager = manager.bg() # больше не можем использовать manager.dialog_manager, потому что он не будет доступен
    logger.trace(f"Payment check task started for user {user_telegram_id}")
    try:
        start_time = datetime.now()
        timeout = timedelta(minutes=CHECK_PAYMENT_TIMEOUT_MINUTES)
        
        while True:
            if datetime.now() - start_time > timeout:
                break
                
            payment_info = yookassa.get_payment(payment_id)
            if payment_info.status == 'waiting_for_capture':
                yookassa.capture_payment(payment_id, payment_info.amount.value)
            if payment_info.status == 'succeeded':
                await _register_success_payment(manager, user_telegram_id=user_telegram_id, months=months, marzban=marzban, referrer_id=referrer_id, balance=balance)    
                return
                
            await asyncio.sleep(5)

        logger.trace(f"Payment check task finished for user {user_telegram_id}")
        await manager.switch_to(BotStates.payment_view)
    except asyncio.CancelledError:
        logger.trace(f"Payment check task cancelled for user {user_telegram_id}")
        await manager.switch_to(BotStates.payment_view)
        raise

async def use_effect(**kwargs):
    dialog_manager = kwargs.get("dialog_manager")
    
    task = asyncio.create_task(_check_payment(dialog_manager))
    dialog_manager.dialog_data["payment_check_task"] = task
    
    return {
        "payment_url": dialog_manager.dialog_data.get("payment_url"),
    }

async def on_cancel(callback: CallbackQuery, button: Button, manager: DialogManager):
    task = manager.dialog_data.get("payment_check_task")
    if task and not task.done():
        task.cancel()

    yookassa: Yookassa = manager.middleware_data.get("yookassa")
    payment_id = manager.dialog_data.get("payment_id")
    
    yookassa.cancel_payment(payment_id)
    await manager.switch_to(BotStates.payment_view)

in_payment_window = Window(
    Const("Ссылка на оплату:"),
    Format("{payment_url}"),
    Button(Const("Отменить"), id="on_cancel", on_click=on_cancel),  
    state=BotStates.in_payment_view,
    getter=use_effect,
)