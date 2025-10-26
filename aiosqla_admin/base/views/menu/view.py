from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List
from aiogram.types import InlineKeyboardButton
from ...handler import BaseHandler

from .handlers import CloseMenu, MenuByCallback, MenuByCommand
from ..base_view import BaseView
from aiogram.fsm.context import FSMContext
from ...callback_data.configs.viewof import BaseViewOf
from aiogram import Router





class BaseMenuView(BaseView):
    def __init__(
            self, 
            command: str, 
            handlers: List[BaseHandler]=None,
            autoclear: bool=True
        ):
        super().__init__(
            BaseViewOf.MENU,
            handlers or [
                MenuByCallback(self, 'callback_query'),
                MenuByCommand(self, 'message'),
                CloseMenu(self, 'callback_query')
            ]
        )

        self.command = command
        self.autoclear = autoclear

        self._menu_btns = None
        self._close_btn = None


    @property
    def close_btn(self):
        if self._close_btn:
            return self._close_btn
        
        cbu = self.ctx.cbu
        cd = cbu.Callback(
            module=self.dashboard.module,
            viewof=self.viewof,
            action=cbu.Action.CLOSE, 
            triggers=cbu.ViewOf.MENU
        ).pack()
        close_btn = InlineKeyboardButton(text='❌ Close', callback_data=cd)

        self._close_btn = close_btn
        return close_btn



    @property
    def menu_btns(self):
        if self._menu_btns:
            return self._menu_btns
        
        cbu = self.ctx.cbu

        keyboard = InlineKeyboardBuilder()
        for schema in self.dashboard.the_schemas:
            model_name = schema.Meta.model.__name__
            cd = cbu.Callback(
                module=self.dashboard.module,
                viewof=cbu.ViewOf.LIST,
                mdl_name=model_name, 
                action=cbu.Action.SHOW
            ).pack()
            keyboard.button(text=model_name, callback_data=cd)
        keyboard.add(self.close_btn)
        keyboard.adjust(3)
        markup = keyboard.as_markup()

        self._menu_btns = markup
        return markup

    
    @property
    def text(self):
        return f"{self.dashboard.module.name} Dashboard:"
    

    async def resolve_menu(self, user_id: int, state: FSMContext):
        if self.autoclear:
            print(f"{self.ctx.memory=}")
            print(f"{type(self.ctx.memory)=}")
            print(f"{self.ctx.memory.describe()=}")
            await self.ctx.memory.dashboard(user_id).clear()
        await state.set_state(None)