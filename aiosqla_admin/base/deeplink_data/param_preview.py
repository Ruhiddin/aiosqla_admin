from aiogram.filters.callback_data import CallbackData
from .action import DeeplinkAction
from aiogram_toolkit.deeplink.generators.parameterized import ParameterizedDeeplinkGenerator

class PreviewParam(CallbackData, ParameterizedDeeplinkGenerator, prefix='PRE', sep='_'):
    action: DeeplinkAction = None
    id: int = None
    reply_msg_id: int = None
    class_name: str = None