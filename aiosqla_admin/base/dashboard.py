from typing import List
from aiogram import Router
from pydantic import BaseModel

from .views.detail.view import BaseDetail
from .views.list.view import BaseList
from .views.menu.view import BaseMenuView
from .callback_data.configs.module import BaseModule


class BaseDashboard:
    def __init__(
            self, 
            module: BaseModule, 
            menu_view: BaseMenuView, 
            # list_view: BaseList, 
            # detail_view: BaseDetail,
            schemas: List[BaseModel]=None, 
            excluded_schemas: List[BaseModel]=None, 
        ):

        assert isinstance(module, BaseModule) is True, f"module should be an istance of aiogram_toolkit.dashbaord.base.callback_data.configs.module.BaseModule but got {type(module)}"
        self.module = module 
        self.router = Router()

        self.menu = menu_view
        # self.list = list_view
        # self.detail = detail_view

        self.schemas = schemas
        self.excluded_schemas = excluded_schemas

        # print(f"{self.menu.router=}")
        # print(f"{type(self.menu)=} {self.menu=}")
        print(f"{self.router.sub_routers=}")
        for view in [self.menu]:
            print("router:", view.router)
            print("type(router):", type(view.router))
            print("isinstance(router, Router):", isinstance(view.router, Router))
            print(f"{view.router.sub_routers=}")

        self.router.include_router(self.menu.router)#s(*[view.router for view in [self.menu]])#, self.list, self.detail]])


    def bind_ctx(self, dashboard_context: "DashboardContext"): # type: ignore  # noqa: F821
        self.ctx = dashboard_context
        for view in (self.menu,):# self.list, self.detail):
            view.bind_dashboard(self)
            view.bind_ctx(dashboard_context)

    @property
    def the_schemas(self):
        if self.schemas is None:
            self.schemas = self.ctx.schemas

        if self.excluded_schemas:
            return [i for i in self.schemas if i not in self.excluded_schemas]
        else:
            return self.schemas
