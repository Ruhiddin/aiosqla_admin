from ..base_view import BaseView
from aiogram_toolkit.dashboard.base.handler import BaseHandler
from aiogram.types import InlineKeyboardButton
from typing import List, Literal
from aiogram_toolkit.dashboard.base.callback_data.configs.viewof import BaseViewOf
from ..menu.handlers import MenuByCallback
from ..detail.handlers import DetailByCallback
from ..feat_filterby.handlers import FilterByCallback
from ..feat_sortby.handlers import SortByCallback
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from ...deeplink_data.param_preview import PreviewParam
from ...deeplink_data.action import DeeplinkAction
from aiogram_toolkit.markdown.wrappers.markdown_v2 import link
from aiogram_toolkit.dashboard.utils.sqla_model import get_current_instance_related_ids
from aiogram.types import Message
from aiogram_toolkit.dashboard.base.callback_data.configs.callback import BaseCallback
from aiogram_toolkit.dashboard.memory.base import BaseCluster
from enum import Enum




class BaseListView(BaseView):
    def __init__(
            self, 
            handlers: List[BaseHandler]=None,
            extra_btns_top: List[List[InlineKeyboardButton]]=[],
            extra_btns_bottom: List[List[InlineKeyboardButton]]=[]

        ):
        super().__init__(
            BaseViewOf.MENU,
            handlers or [
                # MenuByCallback(self, 'callback_query'),
                # MenuByCommand(self, 'message'),
                # CloseMenu(self, 'callback_query')
            ]
        )
        self.extra_btns_top = extra_btns_top
        self.extra_btns_bottom = extra_btns_bottom
    
    async def select_page_data(self, Model, page: int, items_per_page: int=10):
        """
        Handles pagination for a SQLAlchemy model.

        :param Model: SQLAlchemy model class for which data is being fetched.
        :param page: Current page number (1-based index).
        :return: stmt (page selection)
        """
        
        offset = (page - 1) * items_per_page

        stmt = select(Model).limit(items_per_page).offset(offset)
        return stmt
    
    def adjust_stmt(self, stmt):
        pass

    async def prepare_page_data(
            stmt, 
            model_name: str, 
            page: int, 
            session: AsyncSession, 
            memory: BaseCluster,
            msg: Message, 
            list_click_mode: bool, 
            Callback: BaseCallback, 
            trigger: Enum, 
            action: Enum, 
            is_selection: bool
        ):
        """
        Fetches paginated page data for a SQLAlchemy model with caching.

        - Retrieves data from FSMContext cache if available.
        - Executes the provided SQLAlchemy statement if the page is not cached.
        - Stores fetched results in FSMContext for future requests.

        :param stmt: SQLAlchemy query statement.
        :param model_name: Name of the model (used for cache key).
        :param page: Page number (1-based index).
        :param session: SQLAlchemy session object.
        :param dashboard: Dashboard cluster instance
        :param msg: Message
        :param list_click_mode: bool
        :param Callback: Aiogram's CallackData util
        :param trigger: Trigger enum option
        :param action: Action enum option
        :param is_selection: bool
        :return: Cached or freshly fetched list of objects.
        """

        page_data = await memory.lists(model_name).pages_data.page_data(page).get()
        if page_data:
            return page_data
        
        await msg.edit_text(f'Downloading {model_name}: {page}-page...')
        ids = await get_current_instance_related_ids(msg, memory, session) if is_selection else []

        page_data = []
        for model in await session.scalars(stmt):
            if list_click_mode:
                url = await PreviewParam(
                    action=DeeplinkAction.MODEL_PREVIEW, 
                    reply_msg_id=msg.message_id, 
                    class_name=model_name, 
                    id=model.id
                ).generate_deeplink(msg.bot)
                string = link(label=model.tg_list_view(), url=url)
            else:
                string = model.tg_list_view()
            
            checkmark = '✅ ' if model.id in ids and is_selection else ''
            string = checkmark + string
            
            page_data.append({
                'string': string,
                'label': str(model.id),
                'cd': Callback(triggers=trigger, action=action, mdl_name=model_name, id=model.id).pack()
            })

        if page_data:
            await memory.lists(model_name).pages_data.page_data(page).set(page_data)
        return page_data
    
    def add_extra_btns_row(
            self, 
            btn_row: List[InlineKeyboardButton]=None, 
            to: Literal["top", 'bottom']=None
        ):
        match to:
            case 'top':
                btns = self.extra_btns_top
            case 'bottom':
                btns = self.extra_btns_bottom
        
        if btn_row is not None and isinstance(btn_row, list):
            for btn in btn_row:
                assert isinstance(btn, InlineKeyboardButton) is True, "btns in row should be instance of InlineKeyboardButton"
            btns.append(btn_row)

    def prepare_extra_btns_top(
            self, 
            click_mode_on: bool, 
            item_count: int, 
            model_name: str, 
            field_name: str
        ):
        cbu = self.ctx.cbu

        is_media = model_name == "Media"
        new_btn_text = "🆕 Add Media ➕" if is_media else "🆕 Create ➕"
        new_btn_cd_action = cbu.Action.SET if is_media else cbu.Action.CREATE
        the_create_btn = InlineKeyboardButton(
            text=new_btn_text,
            callback_data=cbu.Callback(
                viewof=self.cbu.ViewOf.DETAIL,
                action=new_btn_cd_action,
                mdl_name=model_name,
                field_name=field_name if is_media else None
            )
        )
        self.add_extra_btns_row(
            [the_create_btn],
            to='top'
        )

        if item_count > 0:
            click_mode_toggle_btn_text = f"View Mode: {"🔗 Click" if click_mode_on else "🔰 Extended"}"
            click_mode_toggle_btn = InlineKeyboardButton(
                text=click_mode_toggle_btn_text, 
                callback_data=cbu.Callback(
                    action=cbu.Action.TOGGLE_CLICK_MODE, 
                    viewof=self.viewof, 
                    mdl_name=model_name
                ).pack()
            )

            self.add_extra_btns_row(
                [
                    click_mode_toggle_btn,
                ],
                to='top'
            )

    def prepare_extra_btns_bottom(
            self,
            is_selection: bool,
        ):
        btn_filterby = FilterByCallback.trigger_btn
        btn_sortby = SortByCallback.trigger_btn

        self.add_extra_btns_row(
            [
                btn_filterby, 
                btn_sortby
            ],
            'bottom'
        )
        

        if is_selection:
            back_btn = DetailByCallback.trigger_btn
            back_btn.text = 'Back 🔙'
        else:
            back_btn = MenuByCallback.trigger_btn
            back_btn.text = "🔙 Back to Menu"
        
        self.add_extra_btns_row(
            [
                back_btn
            ],
            'bottom'
        )

    def do_list_sort(self):
        pass
    def do_list_filter(self):
        pass