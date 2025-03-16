from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, DialogManager, StartMode
from datetime import datetime
from states import BotStates

async def use_effect(**kwargs):
    dialog_manager = kwargs.get("dialog_manager")
    balance = dialog_manager.middleware_data.get("balance")
    user_id = dialog_manager.event.from_user.id

    history = []
    raw_history = await balance.get_history(user_id, 5)
    for transaction in raw_history:
        transaction_type = "+" if transaction['type'] == 'income' else "-"
        formatted_value = f"{transaction_type}{abs(transaction['value'])}"
        formatted_date = datetime.fromisoformat(str(transaction['timestamp'])).strftime("%d.%m.%Y %H:%M")
        
        history.append(
            f"{formatted_date} | {formatted_value:>8} RUB | {transaction['note']}"
        )

    return {
        "my_balance_rub": await balance.get_balance(user_id),
        "balance_history": "\n".join(history) if history else "No transactions yet",
    }

async def on_copy_referral_link(callback: CallbackQuery, button: Button, manager: DialogManager):
    bot = manager.event.bot
    link = manager.middleware_data.get("referral")
    link = await link.get_referral_link(bot, manager.event.from_user.id)
    link = "`" + link + "`"
    await callback.message.answer(text=link, parse_mode="Markdown")

async def on_back(callback: CallbackQuery, button: Button, manager: DialogManager):
    marzban = manager.middleware_data.get("marzban")
    if await marzban.user_active(manager.event.from_user.id):
        await manager.switch_to(BotStates.subscription_view)
    else:
        await manager.switch_to(BotStates.payment_view)

referral_system_window = Window(  
        Const("Начислим 20% от каждой оплаты вашим рефералом.  Если реферал оплачивает подписку каждый месяц, то вы получаете 40 руб каждый месяц."),
        Format("Баланс: {my_balance_rub} RUB\n"), 
        Format("5 последних действий:\n{balance_history}"),
        Button(Const("Копировать реферальную ссылку"), id="on_copy_referral_link", on_click=on_copy_referral_link),  
        Button(Const("Назад"), id="on_back", on_click=on_back),  
        state=BotStates.referral_system_view,
        getter=use_effect,
    )