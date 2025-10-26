from functools import wraps
from aiogram.filters.callback_data import CallbackData




def module_sensitive(filter_func):
    """Allow other filter to run if Callback.module is correct."""
    @wraps(filter_func)
    def wrapper(self, cd: CallbackData):
        if cd.module == self.dashboard.module:
            return filter_func(self, cd)
        else:
            return False
    return wrapper

def viewof_sensitive(filter_func):
    """Allow other filter to run if Callback.viewof is correct."""
    @wraps(filter_func)
    def wrapper(self, cd: CallbackData):
        if cd.viewof == self.view.viewof:
            return filter_func(self, cd)
        else:
            return False
    return wrapper

