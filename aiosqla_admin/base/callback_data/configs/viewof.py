from enum import Enum


class BaseViewOf(int, Enum):
    MENU = 1
    DETAIL = 2
    LIST = 3
