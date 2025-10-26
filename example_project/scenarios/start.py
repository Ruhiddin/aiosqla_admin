from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import CommandStart



start_router = Router()



@start_router.message(CommandStart())
async def start(msg: Message):
    await msg.reply(f"Hi, {msg.from_user.first_name} {msg.from_user.last_name}!\n\nWelcome!")