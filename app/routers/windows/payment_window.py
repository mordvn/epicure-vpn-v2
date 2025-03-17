from aiogram_dialog import Window, DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Back
from aiogram.types import CallbackQuery
from datetime import datetime, timedelta
from states import BotStates
from services.yookassa import Yookassa
from services.marzban import Marzban
from config import settings
import random
from loguru import logger
from routers.windows.in_payment_window import _register_success_payment
from services.balance import Balance
from services.referral import ReferralSystem

async def on_pay(callback: CallbackQuery, button: Button, manager: DialogManager, months: int):
    user_telegram_id = manager.event.from_user.id
    yookassa: Yookassa = manager.middleware_data.get("yookassa")
    balance: Balance = manager.middleware_data.get("balance")
    marzban: Marzban = manager.middleware_data.get("marzban")
    referral: ReferralSystem = manager.middleware_data.get("referral")

    price = settings.PAYMENT_SUBSCRIBTION_PRICE_RUB * months

    if not await balance.enough_balance(user_telegram_id, price):
        order_key = f"{user_telegram_id}_{random.randint(1000,9999)}"
        payment_id, payment_url, amount = yookassa.create_payment(price, order_key)
        
        manager.dialog_data.update(payment_id=payment_id, payment_url=payment_url, amount=amount, months=months)
        await manager.switch_to(BotStates.in_payment_view)
    else:
        await balance.register_expense(
            user_id=user_telegram_id, 
            value=price, 
            note=f"Оплата {months} месяцев подписки"
        )

        referrer_id = await referral.get_referrer(user_telegram_id)
        await _register_success_payment(manager, user_telegram_id=user_telegram_id, months=months, marzban=marzban, referrer_id=referrer_id, balance=balance)

        await callback.message.answer(text=f"С внутреннего баланса списано {price} RUB")
        await manager.switch_to(BotStates.subscription_view)

async def on_pay_1_month(callback: CallbackQuery, button: Button, manager: DialogManager):
    await on_pay(callback, button, manager, months=1)
async def on_pay_3_months(callback: CallbackQuery, button: Button, manager: DialogManager):
    await on_pay(callback, button, manager, months=3)
async def on_pay_6_months(callback: CallbackQuery, button: Button, manager: DialogManager):
    await on_pay(callback, button, manager, months=6)
async def on_pay_referral(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(BotStates.referral_system_view)

payment_window = Window(
        Const("❌ Подписка не активирована."),      
        Const("После оплаты бот отправит ссылку, которую добавляют в XRay клиент, после чего используют VPN."),      
        Const(f"Подписка VLESS Германия 150 ГБ до 150 ГБ/сек за {settings.PAYMENT_SUBSCRIBTION_PRICE_RUB} рублей в месяц"),      
        Button(Const("Оплатить 1 месяц"), id="on_pay_1_month", on_click=on_pay_1_month),  
        Button(Const("Оплатить 3 месяца"), id="on_pay_3_months", on_click=on_pay_3_months),  
        Button(Const("Оплатить 6 месяцев"), id="on_pay_6_months", on_click=on_pay_6_months),  
        Button(Const("Реферальная система"), id="on_pay_referral", on_click=on_pay_referral),  
        state=BotStates.payment_view,
    )