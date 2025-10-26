from typing import Any, Optional

from aiogram.filters.callback_data import CallbackData

from .action import BaseAction
from .viewof import BaseViewOf
from .module import BaseModule


class BaseCallback(CallbackData, prefix='dash'):
    module: Optional[BaseModule] = None
    viewof: Optional[BaseViewOf] = None
    action: Optional[BaseAction] = None
    mdl_name: Optional[str] = None
    field_name: Optional[str] = None
    option_set: Optional[Any] = None
    id: Optional[int] = None