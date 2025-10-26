from .base_renderer import UIFieldRenderer
from typing import Optional
from aiogram.types import InlineKeyboardButton


class DefaultFieldRenderer(UIFieldRenderer):
    async def render_text(self) -> str:
        from utils.utils_markdown.markdown_v2_utils import b
        from utils.utils_markdown.normalization import normalize_markdown_v2 as nm2
        from utils.utils_link.param_utils import get_preview_link
        from constants.regex import DT_FORMATS
        from enum import Enum

        field_type = self.data.get("type")
        value = self.data.get("value")
        required = self.data.get("required", False)
        read_only = self.data.get("read_only", False)
        class_name = self.data.get("class_name")
        bot = self.ctx["bot"]
        reply_msg_id = self.ctx.get("reply_msg_id")

        label = b(self.field_name, escape=True)

        if field_type == "rel_many":
            items = self.data.get("values", [])
            if "media" in self.field_name:
                links = [
                    await get_preview_link(bot, self.ctx["SP_Action"].MEDIA_PREVIEW, reply_msg_id, i["id"], class_name)
                    for i in items
                ]
                value = ", ".join(links)
            else:
                links = [
                    await get_preview_link(bot, self.ctx["SP_Action"].MODEL_PREVIEW, reply_msg_id, id, class_name)
                    for id in items
                ]
                value = ", ".join(links)

        elif field_type == "rel_single" and value:
            url = await get_preview_link(bot, self.ctx["SP_Action"].MODEL_PREVIEW, reply_msg_id, value, class_name)
            value = f"[{value}]({url})"

        elif isinstance(field_type, type) and issubclass(field_type, Enum):
            value = getattr(value, "label", None) or getattr(value, "value", None)

        elif field_type == "datetime" and value:
            value = value.strftime(DT_FORMATS["dotted"]["regex"])

        value = nm2(str(value)) if value else ("⚠️" if required else nm2("[ ]"))
        return f"{label}: {value}"

    async def render_button(self) -> Optional[InlineKeyboardButton]:
        if self.data.get("read_only"):
            return None
        if self.field_name in self.ctx.get("excluded_btns", []):
            return None

        cb_factory = self.ctx["Callback"]
        triggers = self.ctx["triggers"]
        action = self.ctx["action"]

        return InlineKeyboardButton(
            text=self.field_name.capitalize(),
            callback_data=cb_factory(triggers=triggers, action=action, field_name=self.field_name.upper()).pack()
        )