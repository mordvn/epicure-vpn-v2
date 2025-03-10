from var_dump import var_dump
from datetime import datetime, timedelta
import logging
logger = logging.getLogger(__name__)

from datetime import date

from aiogram import Router, types
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram import Router
from aiogram.types import LabeledPrice, PreCheckoutQuery
from aiogram import F
import random
from services.marzban import Marzban
from services.youkassa import Youkassa
from config import settings
from keyboards import payment_link_keyboard
from states import PaymentState, SubscriptionState
from aiogram.fsm.context import FSMContext

start_router = Router()

@start_router.message(CommandStart())
async def process_cmd_start(message: Message, marzban: Marzban, youkassa: Youkassa, state: FSMContext):
    await state.clear()

    try:
        if await marzban.user_active(message.from_user.id): 
            await send_subscribtion_link(message, marzban, state)
        else:
            await send_payment_link(message, youkassa, state)
    except Exception as e:
        await message.answer(f"Error: {e}")

@start_router.message(Command("help"))
async def process_cmd_help(message: Message):
    await message.answer("help-command")


async def send_subscribtion_link(message: Message, marzban: Marzban, state: FSMContext):
    user_telegram_id = message.from_user.id
    marz_user = await marzban.get_user(user_telegram_id)
    link = marz_user.links[0]
    await message.answer(text=f'your link:\n{link}\ninfo:\n{str(marz_user)}')

    await state.set_state(SubscriptionState.in_subscription_view)

async def send_payment_link(message: Message, youkassa: Youkassa, state: FSMContext):
    payment_id, payment_url, amount = youkassa.create_payment(settings.PAYMENT_SUBSCRIBTION_PRICE_RUB, f"{str(message.from_user.id)}_{random.randint(1000,9999)}")
    await message.answer(text=f'payment link:\n{payment_url}\namount: {amount} rub', reply_markup=payment_link_keyboard(payment_url))

    await state.set_state(PaymentState.in_payment_view)
    await state.update_data(payment_id=payment_id, payment_url=payment_url, amount=amount)


async def process_success_payment(message: Message, marzban: Marzban, state: FSMContext):
    await state.clear()

    user_telegram_id = message.from_user.id

    if await marzban.user_active(user_telegram_id):
        marz_user = await marzban.get_user(user_telegram_id)
        new_sub_finish_time = int((datetime.fromtimestamp(marz_user.expire) + timedelta(days=settings.PAYMENT_SUBSCRIBTION_PERIOD_DAYS)).timestamp())
        await marzban.update_user(str(user_telegram_id), new_sub_finish_time, settings.SUBSCRIBTION_DATA_LIMIT_KB)
    else:
        new_sub_finish_time = int((datetime.now() + timedelta(days=settings.PAYMENT_SUBSCRIBTION_PERIOD_DAYS)).timestamp())
        await marzban.create_user(str(user_telegram_id), new_sub_finish_time, settings.SUBSCRIBTION_DATA_LIMIT_KB)

    await send_subscribtion_link(message, marzban, state)