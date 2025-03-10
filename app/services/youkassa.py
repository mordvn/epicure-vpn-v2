
from yookassa import Payment
from yookassa.domain.models.currency import Currency
from yookassa.domain.common.confirmation_type import ConfirmationType
from yookassa.domain.request.payment_request_builder import PaymentRequestBuilder
from yookassa import Configuration
from config import settings
import var_dump as var_dump
Configuration.configure(settings.YOO_KASSA_SHOP_ID, settings.YOO_KASSA_SECRET_KEY)

class Youkassa:
    """https://github.com/yoomoney/yookassa-sdk-python/blob/master/docs/examples/02-payments.md
    https://yookassa.ru/docs/payment-solution/payments/testing-and-examples/testing"""
    def create_payment(self, amount: int, order_number: str):
        builder = PaymentRequestBuilder()
        builder.set_amount({"value": amount, "currency": Currency.RUB}) \
            .set_confirmation({"type": ConfirmationType.REDIRECT, "return_url": settings.YOO_KASSA_RETURN_URL}) \
            .set_capture(False) \
            .set_description(f"order: {order_number}") \
            .set_metadata({"orderNumber": order_number}) \
        
        request = builder.build()
        res = Payment.create(request)

        return (res.id, res.confirmation.confirmation_url, res.amount.value)

    def get_payment(self, payment_id: str):
        res = Payment.find_one(payment_id)
        return res
    
    def capture_payment(self, payment_id: str, amount: float):
        params = {
            "amount": {
                "value": str(amount),
                "currency": "RUB"
            }
        }
        res = Payment.capture(payment_id, params)
        return res
        
