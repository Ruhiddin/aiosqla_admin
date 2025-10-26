from typing import Any, Dict, List, Optional
from .field.default_renderer import DefaultFieldRenderer
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


class UITextGenerator:
    def __init__(
        self,
        renderer_cls=DefaultFieldRenderer,
        btn_group_size: int = 2,
    ):
        self.renderer_cls = renderer_cls
        self.btn_group_size = btn_group_size

    async def generate(
        self,
        ui_data: Dict[str, Dict[str, Any]],
        context: Dict[str, Any],
        only_field: Optional[str] = None,
        markup: bool = True,
        extra_btns: Optional[Dict[str, List[List[InlineKeyboardButton]]]] = None,
    ):
        kb = InlineKeyboardBuilder()
        text_lines = []
        btns = []

        extra_btns = extra_btns or {}
        excluded_btns = context.get("excluded_btns", [])

        # top extra buttons
        for row in extra_btns.get("top_rows", []):
            kb.row(*row)

        for field_name, field_data in ui_data.items():
            if only_field and field_name != only_field:
                continue

            context["excluded_btns"] = excluded_btns
            renderer = self.renderer_cls(field_name, field_data, context)

            text = await renderer.render_text()
            text_lines.append(text)

            if markup:
                btn = await renderer.render_button()
                if btn:
                    btns.append(btn)

        # group main buttons
        for i in range(0, len(btns), self.btn_group_size):
            kb.row(*btns[i:i + self.btn_group_size])

        # bottom extra buttons
        for row in extra_btns.get("bottom_rows", []):
            kb.row(*row)

        return "\n".join(text_lines), kb.as_markup() if markup else None
