from loguru import logger
from aiogram_dialog import (
    DialogManager, StartMode
)
from aiogram.types import Message
from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.utils.deep_linking import decode_payload
from states import BotStates
from services.marzban import Marzban
from services.referral import ReferralSystem
router = Router()

async def _set_referrer(message: Message, dialog_manager: DialogManager, referral: ReferralSystem, command: CommandObject):
    if payload := command.args:
        payload = decode_payload(payload)
        logger.trace(f"referrer_telegram_id: {payload}")
        await referral.set_referrer(message.from_user.id, payload)

@router.message(CommandStart())
@router.message(CommandStart(deep_link=True))
async def start(message: Message, dialog_manager: DialogManager, command: CommandObject, marzban: Marzban, referral: ReferralSystem):
    try:
        if await marzban.user_active(message.from_user.id):
            await dialog_manager.start(BotStates.subscription_view, mode=StartMode.RESET_STACK)
        else:
            await _set_referrer(message, dialog_manager, referral, command)

            await dialog_manager.start(BotStates.payment_view, mode=StartMode.RESET_STACK)
    except Exception:
        logger.exception("An error occurred when /start command was executed")
        raise