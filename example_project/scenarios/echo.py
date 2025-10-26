from aiogram import Router
from aiogram.types import Message


echo_router = Router()

@echo_router.message()
async def echo(msg: Message):
    await msg.forward(msg.chat.id, msg.message_thread_id)