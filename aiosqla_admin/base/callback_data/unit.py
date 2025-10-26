from .configs.module import BaseModule
from .configs.callback import BaseCallback
from .configs.viewof import BaseViewOf
from .configs.action import BaseAction


class BaseCallbackUnit:
    Module = BaseModule
    Callback = BaseCallback
    ViewOf = BaseViewOf
    Action = BaseAction
