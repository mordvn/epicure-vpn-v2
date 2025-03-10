from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def payment_link_keyboard(link: str):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Перейти к оплате", url=link)],
        [InlineKeyboardButton(text="оплатил", callback_data="check_payment")],
    ])
    return kb

