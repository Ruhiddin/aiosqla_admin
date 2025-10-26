from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from base import bot
from database.enums import FileType
from utils.callback_data import SP_Action, SP_PreviewParam
from utils.param_shortcut_utils import P_PM
from utils.utils_link.param_utils import get_preview_link
from utils.utils_markdown.markdown_v2_utils import link
from utils.utils_markdown.normalization import normalize_markdown_v2 as nm2
from utils.utils_model.model_utils import model_string_map


# ==============______MEDIA PREVIEW______=========================================================================================== MEDIA PREVIEW
async def media_preview(msg: Message, pd: SP_PreviewParam, session: AsyncSession, close_btn: InlineKeyboardMarkup):
    await msg.delete()
    instance = await session.get(model_string_map['Media'], pd.id)
    if not instance:
        return
    
    chat_id = msg.chat.id
    rel_class_name = instance.rel_class.value
    rel_id = instance.rel_id
    title = f"{rel_class_name}-{rel_id}"
    rel_url = await get_preview_link(msg.bot, action=SP_Action.MODEL_PREVIEW, reply_msg_id=pd.reply_msg_id, class_name=rel_class_name, id=rel_id)
    rel_link = link(title, rel_url)

    text = (
        f"{nm2(instance.media_type)} {nm2(instance.file_type)}"
        f"{rel_link}"
    )
    file_title = f"{instance.media_type} {instance.file_type}"
    file_id = instance.file_id

    params = {
        **{
            'chat_id': chat_id,
            'reply_to_message_id': pd.reply_msg_id,
            'caption': text,
            'reply_markup': close_btn
        },
        **P_PM
    
    }
    try:
        match instance.file_type:
            case FileType.PHOTO:
                await bot.send_photo(photo=file_id, **params)
            case FileType.DOCUMENT:
                await bot.send_document(document=file_id, **params)
            case FileType.VIDEO:
                await bot.send_video(video=file_id, **params)
            case FileType.VIDEO_NOTE:
                params.pop('parse_mode', None)
                await bot.send_video_note(video_note=file_id, **params)
            case FileType.AUDIO:
                await bot.send_audio(audio=file_id, title=file_title, **params)
            case FileType.VOICE:
                await bot.send_voice(voice=file_id, **params)
            case __:
                raise ValueError("MEDIA FILE TYPE NOT SUPPORTED")
            
    except TelegramBadRequest as e:
        text = f"{instance.file_type.value}-{id}: {e}"
        await bot.send_message(chat_id, reply_to_message_id=pd.reply_msg_id, text=text, reply_markup=close_btn)




