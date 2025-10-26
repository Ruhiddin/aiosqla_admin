from aiogram.filters.callback_data import CallbackData
from .action import DeeplinkAction
from typing import Optional
from aiogram_toolkit.deeplink.generators.parameterized import ParameterizedDeeplinkGenerator



class ReferralParam(CallbackData, ParameterizedDeeplinkGenerator, prefix='REF', sep='_'):
    action: Optional[DeeplinkAction] = DeeplinkAction.REFFERAL
    referrer_id: Optional[int] = None