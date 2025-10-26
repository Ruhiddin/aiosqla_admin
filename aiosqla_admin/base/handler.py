from typing import Callable, Any, Literal
from aiogram.types import InlineKeyboardButton
# from aiogram.filters.callback_data import CallbackData



class BaseHandler:
    def __init__(self, view: "BaseView", event_type: Literal['message', 'callback_query']): # type: ignore  # noqa: F821
        self.view = view
        self.event_type = event_type
        self._filter = self._build_filter()
        self._handler = self._build_handler()

    def filter_logic(self, event: Any) -> Any:
        """Override this to implement the actual filter logic."""
        raise NotImplementedError("Subclasses must implement `filter_logic`.")

    def handler_logic(self, event: Any, *args, **kwargs) -> Any:
        """Override this to implement the handler logic."""
        raise NotImplementedError("Subclasses must implement `handler_logic`.")

    def _build_filter(self) -> Callable:
        async def _filter(event):
            return await self.filter_logic(event)
        return _filter

    def _build_handler(self) -> Callable:
        async def _handler(event, *args, **kwargs):
            return await self.handler_logic(event, *args, **kwargs)
        return _handler

    # def is_module_correct(self, cd: CallbackData) -> bool:
    #     return cd.module == self.dashboard.module
    # def is_viewof_correct(self, cd: CallbackData) -> bool:
    #     return cd.viewof == self.view.viewof
    
    def bind_dashbaord(self, dashboard: "BaseDashboard"): # type: ignore  # noqa: F821
        self.dashboard = dashboard
    def bind_ctx(self, ctx: "DashboardContext"): # type: ignore  # noqa: F821
        self.ctx = ctx

    @property
    def trigger_btn(self) -> InlineKeyboardButton:
        raise NotImplementedError

    @property
    def filter(self) -> Callable:
        return self._filter

    @property
    def handler(self) -> Callable:
        return self._handler