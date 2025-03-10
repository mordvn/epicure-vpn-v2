from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import F
from services.youkassa import Youkassa
from routers.start import process_success_payment
from states import PaymentState
from services.marzban import Marzban
from var_dump import var_dump
payment_router = Router()

@payment_router.callback_query(F.data == "check_payment", PaymentState.in_payment_view)
async def process_payment_view(callback: CallbackQuery, state: FSMContext, marzban: Marzban, youkassa: Youkassa):
    data = await state.get_data()

    payment_id = data["payment_id"]
    amount = data["amount"]

    payment_info1 = youkassa.get_payment(payment_id)

    if payment_info1.status == 'waiting_for_capture':

        youkassa.capture_payment(payment_id, amount)

        payment_info2 = youkassa.get_payment(payment_id)

        if payment_info2.status == 'succeeded':
            await callback.message.answer(text='Оплата прошла успешно')
            await process_success_payment(callback.message, marzban, state)
        else:
            await callback.message.answer(text='Попробуйте позже')
            var_dump(payment_info2)
    else:
        await callback.message.answer(text='Попробуйте позже')
        var_dump(payment_info1)
