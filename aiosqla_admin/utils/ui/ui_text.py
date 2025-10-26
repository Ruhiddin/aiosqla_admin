from enum import Enum
from typing import Any, Dict, List

from aiogram import Bot
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from base import log
from constants.misc import MM_DETAIL_BTNS_PER_ROW
from constants.regex import DT_FORMATS

# from utils.callback_data import MMAction, MMCallback, MMTriggers
from utils.callback_data import SP_Action
from utils.utils_link.param_utils import get_preview_link
from utils.utils_markdown.markdown_v2_utils import b, link
from utils.utils_markdown.normalization import normalize_markdown_v2 as nm2


# ====================================================================================================
# ==============             DECORATORS             ==============#
# ====================================================================================================
def create_keyboard_and_apply_extra_btns(func):
    async def wrapper(*args, **kwargs):
        kb: InlineKeyboardBuilder = kwargs.pop('keyboard', InlineKeyboardBuilder())
        extra_btns = kwargs.pop('extra_btns', {})
        group_size = kwargs.pop('group_size', MM_DETAIL_BTNS_PER_ROW)
        markup = kwargs.get('markup', True)

        if extra_btns:
            top_rows = extra_btns.get('top_rows', [])
            for row in top_rows:
                kb.row(*row)

        text, btns = await func(*args, **kwargs)
        for i in range(0, len(btns), group_size):
            row = btns[i:i + group_size]
            kb.row(*row)

        if extra_btns:
            bottom_rows = extra_btns.get('bottom_rows', [])
            for row in bottom_rows:
                kb.row(*row)

        if markup:
            result = text, kb.as_markup()
        else:
            result = text

        # log.magenta.bold.underline.on_white(f"{'UI MSG GENERATED':_>150}")
        # log.magenta.bold(f"{type(result)}:")
        # log.magenta(result)
        # log.magenta(f"{'':_>150}")

        return result

    return wrapper





# ====================================================================================================
# ==============             GET PREVIEW MESSAGE             ==============#
# ====================================================================================================
@create_keyboard_and_apply_extra_btns
async def get_preview_msg(
    ui_data: Dict[str, Dict[str, Any]],
    bot: Bot,
    reply_msg_id: int = None,
    markup: bool = True,
    excluded_btns: List[str] = None,
    extra_btns: Dict[str, List[List[InlineKeyboardButton]]] = None,
    only_field: str = None,
    Callback: CallbackData = None,
    triggers: Enum = None,
    action: Enum = None,
):
    """
    ### Generate message preview text and inline markup for UI data.

    #### Parameters:
    - `ui_data`: Dict[str, Dict[str, Any]] — Field data with metadata and values.
    - `bot`: Bot - Aiogram bot type
    - `reply_msg_id`: int - message id to reply
    - `markup`: bool — Whether to generate inline buttons.
    - `excluded_btns`: Optional[List[str]] — Field names to exclude from buttons.
    - `extra_btns`: Optional[Dict[str, List[List[InlineKeyboardButton]]]] — Extra buttons to append.
    - `only_field`: Optional[str] — If set, renders only the given field.
    - `Callback`: CallbackData — Callback factory for button generation.
    - `triggers`: Enum — Trigger enum used in callback data.
    - `action`: Enum — Action enum used in callback data.

    #### Returns:
    - Tuple[str, List[InlineKeyboardButton]] — Text and inline keyboard buttons.
    """

    excluded_btns = excluded_btns or []
    extra_btns = extra_btns or {}

    text_lines = []
    btns = []

    for field_name, field_data in ui_data.items():
        if only_field and only_field != field_name:
            continue

        field_type = field_data.get('type')
        required = field_data.get('required', False)
        is_read_only = field_data.get('read_only', False)
        class_name = field_data.get('class_name', 'Unknown class') if field_type in {'rel_single', 'rel_many'} else None

        # Handle value based on field type
        if field_type == 'rel_many':
            items = field_data.get('values', [])
            if 'media' in field_name:
                value = [
                    link(
                        label=f"{i['file_type']}-{i['id']}",
                        url=await get_preview_link(
                            bot, SP_Action.MEDIA_PREVIEW, reply_msg_id, i['id'], class_name
                        )
                    )
                    for i in items
                ]
            else:
                value = [
                    link(
                        label=f"{class_name}-{id}",
                        url=await get_preview_link(
                            bot, SP_Action.MODEL_PREVIEW, reply_msg_id, id, class_name
                        )
                    )
                    for id in items
                ]
            value = ', '.join(value) if value else nm2("[ ]")

        elif field_type == 'rel_single':
            id = field_data.get('value')
            if id:
                repr = field_data.get('repr', str(id))
                url = await get_preview_link(
                    bot, SP_Action.MODEL_PREVIEW, reply_msg_id, id, class_name
                )
                value = link(label=repr, url=url)
            else:
                value = None

        elif isinstance(field_type, type) and issubclass(field_type, Enum):
            val = field_data.get('value')
            value = nm2(getattr(val, 'label', None) or getattr(val, 'value', None))

        elif field_type == 'datetime':
            dt = field_data.get('value')
            value = nm2(dt.strftime(DT_FORMATS['dotted']['regex'])) if dt else None

        else:
            value = nm2(field_data.get('value'))

        label = b(field_name, escape=True)
        value = '⚠️' if required and not value and markup else value
        text_lines.append(f"{label}: {value}")

        if markup and not is_read_only and field_name not in excluded_btns:
            btn = InlineKeyboardButton(
                text=field_name.capitalize(),
                callback_data=Callback(
                    triggers=triggers,
                    action=action,
                    field_name=field_name.upper()
                ).pack()
            )
            btns.append(btn)

    return "\n".join(text_lines), btns






# ==============______EXCLUDE MEDIA BTNS______=========================================================================================== EXCLUDE MEDIA BTNS
def get_excluded_media_btns(instance_data: dict):
    media_btns = []
    for field_name in instance_data:
        if field_name.endswith('medias'):
            media_btns.append(field_name)
    
    if instance_data['id'] is None:
        excluded_btns = media_btns
    else:
        excluded_btns = []
    
    return excluded_btns