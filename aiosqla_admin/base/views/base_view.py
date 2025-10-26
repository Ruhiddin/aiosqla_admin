from typing import List
from aiogram import Router
from ..handler import BaseHandler
from ..callback_data.configs.viewof import BaseViewOf


class BaseView:
    def __init__(self, viewof: BaseViewOf, handlers: List[BaseHandler]):
        self.viewof = viewof
        self.router = Router()
        self.handlers = handlers

        #register and bound handlers
        for handler in self.handlers:
            if not isinstance(handler, BaseHandler):
                raise TypeError(f"Expected BaseHandler, got {type(handler)}")

            if handler.event_type == "message":
                self.router.message.register(handler.handler, handler.filter)
            elif handler.event_type == "callback_query":
                self.router.callback_query.register(handler.handler, handler.filter)
            else:
                raise NotImplementedError(f"Unsupported event type: {handler.event_type}")
            
    
    def bind_dashboard(self, dashboard: "Dashboard"): # type: ignore  # noqa: F821
        self.dashboard = dashboard
        for handler in self.handlers:
            handler.bind_dashbaord(dashboard)
    
    def bind_ctx(self, ctx: "DashboardContext"): # type: ignore  # noqa: F821
        self.ctx = ctx
        for handler in self.handlers:
            handler.bind_ctx(ctx)

