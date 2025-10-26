import sys
import asyncio
import logging
from aiogram import Dispatcher
from aiogram.fsm.strategy import FSMStrategy
from aiogram.fsm.storage.memory import MemoryStorage
# from ..middlewares.preview import PreviewMiddleware
# from ..callback_data
from .base import bot
from .scenarios.router import scenarios_router

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    dp = Dispatcher(fsm_strategy=FSMStrategy.CHAT_TOPIC, storage=MemoryStorage())
    dp.include_routers(scenarios_router)

    # dp.message.middleware(PreviewMiddleware({
    #     SomeData: handle_some,
    #     OtherData: handle_other,
    # }))


    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())