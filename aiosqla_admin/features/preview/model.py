from datetime import datetime, timezone

from aiogram.types import InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from db_redis.real.root_cluster import get_root
from utils.callback_data import SP_PreviewParam
from utils.long_message_utils import send_long_message
from utils.utils_mm.detail_utils.preview_msg_utils import get_preview_msg
from utils.utils_mm.detail_utils.ui_data_utils import get_ui_data
from utils.utils_model.model_utils import model_string_map


# ==============______MODEL PREVIEW______=========================================================================================== MODEL PREVIEW
async def model_preview(msg: Message, pd: SP_PreviewParam, session: AsyncSession, close_btn: InlineKeyboardMarkup):
    await msg.delete()
    
    instance = await session.get(model_string_map.get(pd.class_name), pd.id)
    if not instance:
        return await msg.answer("Model not found", reply_markup=close_btn)
    # try:
    model_data = await get_ui_data(instance)
    text, __ = await get_preview_msg(model_data, msg.bot, pd.reply_msg_id, False)
    root = get_root()
    await send_long_message(
        msg.bot, 
        msg.chat.id, 
        text, 
        msg.message_id, 
        msg.from_user.id, 
        False, 
        True, 
        False, 
        close_btn,
        root=root
    )
    # except Exception as e:
    #     text = f"{pd.class_name}-{pd.id}: {e}"
    #     await bot.send_message(msg.chat.id, reply_to_message_id=pd.reply_msg_id, text=text, reply_markup=close_btn)