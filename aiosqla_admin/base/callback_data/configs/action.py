from enum import Enum


class BaseAction(int, Enum):
    FIRST_SHOW = 0
    SHOW = 1
    CLOSE = 3
    PG = 4

    CREATE = 5
    SINGLE_SELECTION = 6
    MULTI_SELECTION = 7

    SET = 8
    OPTION_SET = 9
    SAVE = 10
    SAVE_CONFIRM = 11

    RESET = 12
    RESET_CONFIRM = 13
    RESET_CANCEL = 14

    BACK_CONFIRM = 15
    BACK = 16
    BACK_CANCEL = 17

    TOGGLE_CLICK_MODE = 18