from aiogram_toolkit.dashboard.base.handler import BaseHandler
from aiogram_toolkit.dashboard.decorators.cd_filters import module_sensitive, viewof_sensitive
from aiogram_toolkit.callback_data.safe_unpack.decorator import safe_cd_unpack_simple
# from aiogram.filters.callback_data import CallbackData
from aiogram_toolkit.dashboard.base.callback_data.configs.callback import BaseCallback




class ListByCallbackHandler(BaseHandler):
    
    @safe_cd_unpack_simple
    @module_sensitive
    @viewof_sensitive
    def filter_logic(self, cd: BaseCallback):
        Action = self.ctx.cbu.Action
        return cd.action == Action.SHOW
    
    def handler_logic(self, event, *args, **kwargs):
        return super().handler_logic(event, *args, **kwargs)