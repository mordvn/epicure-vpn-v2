from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, DialogManager
from datetime import datetime
from states import BotStates
from services.balance import Balance
from services.referral import ReferralSystem
from services.marzban import Marzban
from config import settings
async def _format_transaction(transaction: dict) -> str:
    transaction_type = "+" if transaction['type'] == 'income' else "-"
    formatted_value = f"{transaction_type}{abs(transaction['value'])}"
    formatted_date = datetime.fromisoformat(str(transaction['timestamp'])).strftime("%d.%m.%Y %H:%M")
    
    return f"{formatted_date} | {formatted_value:>8} RUB | {transaction['note']}"

async def use_effect(**kwargs):
    dialog_manager = kwargs.get("dialog_manager")
    balance: Balance = dialog_manager.middleware_data.get("balance")

    telegram_user_id = dialog_manager.event.from_user.id

    raw_history = await balance.get_history(telegram_user_id, 5)
    history = [await _format_transaction(transaction) for transaction in raw_history]

    return {
        "balance": await balance.get_balance(telegram_user_id),
        "balance_history": "\n".join(history) if history else "No transactions yet",
    }

async def on_copy_referral_link(callback: CallbackQuery, button: Button, manager: DialogManager):
    bot = manager.event.bot
    referral: ReferralSystem = manager.middleware_data.get("referral")

    text = await referral.get_referral_link(bot, manager.event.from_user.id)
    link = "`" + text + "`"
    await callback.message.answer(text=link, parse_mode="Markdown")

async def on_back(callback: CallbackQuery, button: Button, manager: DialogManager):
    marzban: Marzban = manager.middleware_data.get("marzban")

    if await marzban.user_active(manager.event.from_user.id):
        await manager.switch_to(BotStates.subscription_view)
    else:
        await manager.switch_to(BotStates.payment_view)

referral_system_window = Window(  
        Const(f"Начислим {settings.REFERRAL_BONUS_PERCENT}% от каждой оплаты вашим рефералом.  Если реферал оплачивает подписку каждый месяц, то вы получаете {settings.REFERRAL_BONUS_RUB} RUB каждый месяц."),
        Format("Баланс: {balance} RUB\n"), 
        Format("5 последних действий:\n{balance_history}"),
        Button(Const("Копировать реферальную ссылку"), id="on_copy_referral_link", on_click=on_copy_referral_link),  
        Button(Const("Назад"), id="on_back", on_click=on_back),  
        state=BotStates.referral_system_view,
        getter=use_effect,
    )