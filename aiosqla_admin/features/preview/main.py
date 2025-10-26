from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from decorators.session import session_manager
from scenarios.start.preview.media import media_preview
from scenarios.start.preview.model import model_preview
from utils.callback_data import SP_Action, SP_PreviewParam

preview_router = Router()



# ==============______PREVIEW CLOSE______=========================================================================================== PREVIEW CLOSE

preview_close_btn = InlineKeyboardBuilder().button(text="❌ Close", callback_data="prev:CLOSE").as_markup()
@preview_router.callback_query(lambda c: c.data == 'prev:CLOSE')
async def close_model_preview(c: CallbackQuery):
    await c.message.delete()


# ==============______HANDLRE PREVIEW______=========================================================================================== HANDLRE PREVIEW
@session_manager('read')
async def handle_preview(msg: Message, pd: SP_PreviewParam, session: AsyncSession):

    if pd.action == SP_Action.MEDIA_PREVIEW:
        func =  media_preview
    elif pd.action == SP_Action.MODEL_PREVIEW:
        func =  model_preview
    
    return await func(msg, pd, session, close_btn=preview_close_btn)


