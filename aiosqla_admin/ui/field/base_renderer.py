from typing import Any, Dict, Optional
from aiogram.types import InlineKeyboardButton

class UIFieldRenderer:
    def __init__(self, field_name: str, field_data: Dict[str, Any], context: Dict[str, Any]):
        self.field_name = field_name
        self.data = field_data
        self.ctx = context  # contains bot, reply_msg_id, etc.

    async def render_text(self) -> str:
        # Default label + value formatting
        raise NotImplementedError

    async def render_button(self) -> Optional[InlineKeyboardButton]:
        # Optional inline button per field
        return None