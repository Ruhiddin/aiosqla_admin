from aiogram import Router
from .start import start_router
from .echo import echo_router
from .dashboard import dashboard_router


scenarios_router = Router()




scenarios_router.include_routers(
    # start_router,
    # echo_router,
    dashboard_router
)