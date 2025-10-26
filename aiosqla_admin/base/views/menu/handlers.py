from aiogram_toolkit.callback_data.safe_unpack.decorator import safe_cd_unpack_simple
from aiogram_toolkit.dashboard.decorators.cd_filters import module_sensitive, viewof_sensitive
from ...handler import BaseHandler
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton


class MenuByCallback(BaseHandler):
    @property
    def trigger_btn(self):
        cbu = self.ctx.cbu
        return InlineKeyboardButton(
            text="Menu",
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



class MenuByCommand(BaseHandler):
    async def filter_logic(self, msg: Message):
        return msg.text == '/' + self.view.command
    
    async def handler_logic(self, msg: Message, state: FSMContext, *args, **kwargs):
        await self.view.resolve_menu(msg.from_user.id, state)
        await msg.reply(self.view.text, reply_markup=self.view.menu_btns)



class CloseMenu(BaseHandler):
    @safe_cd_unpack_simple
    @module_sensitive
    @viewof_sensitive
    async def filter_logic(self, cd: CallbackData):
        cbu = self.ctx.cbu
        return cd.action == cbu.Action.CLOSE

    async def handler_logic(self, c: CallbackQuery, state: FSMContext, *args, **kwargs):
        await c.message.edit_text(f"{self.dashboard.module.name} Dashboard closed!")
        await self.view.resolve_menu(c.from_user.id, state)