from aiogram.fsm.state import StatesGroup, State

class PaymentState(StatesGroup):
    in_payment_view = State()

class SubscriptionState(StatesGroup):
    in_subscription_view = State()
