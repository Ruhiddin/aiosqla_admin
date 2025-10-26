# from aiosqla_admin.dashboard_context import DashboardContext
from aiosqla_admin.dashboard_context import DashboardContext
from aiosqla_admin.base.dashboard import BaseDashboard
from aiosqla_admin.base.views.menu.view import BaseMenuView
# from aiosqla_admin.base.views.list.view import BaseList
# from aiosqla_admin.base.views.detail.view import BaseDetail
from aiosqla_admin.memory.provider import MemoryProvider
from aiosqla_admin.base.callback_data.unit import BaseCallbackUnit
from aiosqla_admin.base.callback_data.configs.module import BaseModule
from example_project.database.schemas import UserSchema, UserPhoneSchema, UserMetaSchema, GradeSchema


memory_provider = MemoryProvider()

print(f"{memory_provider=}")
print(f"{memory_provider.cluster=}")
print(f"{memory_provider.cluster.describe()=}")

dashboard_context = DashboardContext(
    memory_provider,
    BaseCallbackUnit,
    [
        UserSchema,
        UserPhoneSchema,
        UserMetaSchema,
        GradeSchema,
    ],
    None,
    None,
    dashboards=[
        BaseDashboard(
            BaseModule.default,
            BaseMenuView('mm'),
            # BaseList(),
            # BaseDetail(),
        )
    ]
)

dashboard_router = dashboard_context.router