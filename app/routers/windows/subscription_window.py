from re import S
from aiogram_dialog import Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Url
from aiogram_dialog.widgets.text import Const, Format
from aiogram.types import CallbackQuery
from states import BotStates
from datetime import datetime
from services.marzban import Marzban
HISTORY_LIMIT = 5

async def _convert_to_gb(value: float) -> float:
    return value / 1024 / 1024 / 1024

async def use_effect(**kwargs):
    dialog_manager: DialogManager = kwargs.get("dialog_manager")
    marzban: Marzban = dialog_manager.middleware_data.get("marzban")

    user_telegram_id = dialog_manager.event.from_user.id

    marz_user = await marzban.get_user(user_telegram_id)
    dialog_manager.dialog_data.update(vless_key=marz_user.links[0])

    return {
        "subscription_end_date": str(datetime.fromtimestamp(marz_user.expire).strftime("%d.%m.%Y")),
        "used_data_gb": f"{await _convert_to_gb(marz_user.used_traffic):.2f}",
        "subscription_data_limit_gb": f"{await _convert_to_gb(marz_user.data_limit):.2f}",
    }

async def on_get_subscription(callback: CallbackQuery, button: Button, manager: DialogManager):
    text = str(manager.dialog_data.get("vless_key"))
    link = "`" + text + "`"
    await callback.message.answer(text=link, parse_mode="Markdown")
    text = "⬆️⬆️⬆️\nНикому не показывай этот ключ! Он предназначен для вас и вашего использования"
    await callback.message.answer(text=text)

async def on_get_referral(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(BotStates.referral_system_view)

subscription_window = Window(
        Format("✅ Подписка активна до {subscription_end_date}"),
        Format("В этом месяце использовано {used_data_gb} из {subscription_data_limit_gb} ГБ"),        
        Button(Const("Получить VLESS ключ"), id="on_get_subscription", on_click=on_get_subscription),
        Url(Const("Инструкция"), Const("https://teletype.in/@forcheckmark/xray")),
        Button(Const("Реферальная система"), id="on_get_referral", on_click=on_get_referral),
        state=BotStates.subscription_view,
        getter=use_effect,
    )
