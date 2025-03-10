from routers.start import start_router
from routers.payment import payment_router
def include_routers(dp):
    dp.include_router(start_router)
    dp.include_router(payment_router)
