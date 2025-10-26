from ...handler import BaseHandler
from aiogram.types import InlineKeyboardButton
from aiogram_toolkit.dashboard.decorators.cd_filters import module_sensitive, viewof_sensitive
from aiogram_toolkit.callback_data.safe_unpack.decorator import safe_cd_unpack_simple
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext


class DetailByCallback(BaseHandler):
    @property
    def trigger_btn(self):
        cbu = self.ctx.cbu
        return InlineKeyboardButton(
            text="Detail",
            callback_data=cbu.Callback(
                viewof=self.view.viewof,
                action=cbu.Action.SHOW,
                module=self.dashboard.module
            ).pack()
        )

    @safe_cd_unpack_simple
    @module_sensitive
    @viewof_sensitive
    async def filter_logic(self, cd: CallbackData):
        return cd.action == self.ctx.cbu.Action.SHOW

    async def handler_logic(self, c: CallbackQuery, state: FSMContext, *args, **kwargs):
        await self.view.resolve_menu(c.from_user.id, state)
        await c.message.reply(self.view.text, reply_markup=self.view.menu_btns)
