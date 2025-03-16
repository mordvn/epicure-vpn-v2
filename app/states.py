from aiogram.filters.state import StatesGroup, State
class BotStates(StatesGroup):
    subscription_view = State()
    payment_view = State()
    in_payment_view = State()
    referral_system_view = State()