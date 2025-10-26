from typing import List

from aiogram import Router
from pydantic import BaseModel

from .memory.provider import MemoryProvider

from .base.callback_data.unit import BaseCallbackUnit
from .base.dashboard import BaseDashboard
from .base.mechanics.dialog import BaseDialog
from .base.mechanics.navigation import BaseNavigation


class DashboardContext:
    def __init__(
            self, 
            memory_provider: MemoryProvider, 
            callback_unit: BaseCallbackUnit,
            schemas: List[BaseModel], 
            navigation: BaseNavigation,
            dialog: BaseDialog,
            dashboards: List[BaseDashboard],
            session_factory: callable
        ):
        self.memory = memory_provider.cluster
        self.cbu = callback_unit
        self.nav = navigation
        self.dialog = dialog
        self.schemas = schemas
        self.dashboards = dashboards
        self.router = Router()
        self.session_factory = session_factory

        if len(self.dashboards) > 1:
            self.router.include_routers([dashboard.router for dashboard in self.dashboards or []])
        else:
            self.router.include_router(self.dashboards[0].router)

        for board in self.dashboards or []:
            board.bind_ctx(self)
