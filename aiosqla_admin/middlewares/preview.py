from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message, Update
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.deep_linking import decode_payload
from typing import Callable, Awaitable, Dict, Type, Any


class PreviewMiddleware(BaseMiddleware):
    def __init__(
        self,
        handlers: Dict[Type[CallbackData], Callable[[Message, CallbackData], Awaitable[Any]]],
    ):
        super().__init__()
        self.handlers = handlers

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        message: Message = event.message

        # Fast path: not a message or not the /start command
        if not message or message.text is None or not message.text.startswith("/start"):
            return await handler(event, data)

        # Extract deep link payload (e.g., "/start <payload>")
        parts = message.text.split(maxsplit=1)
        if len(parts) != 2:
            return await handler(event, data)

        encoded = parts[1]
        try:
            decoded = decode_payload(encoded)
        except Exception:
            await message.answer("Invalid start parameter.")
            return

        # Try to match a known param schema
        for Param in self.handlers.keys():
            try:
                unpacked = Param.unpack(decoded)
                start_handler = self.handlers.get(Param)
                if start_handler:
                    return await start_handler(message, unpacked)
            except (TypeError, ValueError):
                continue

        await message.answer("Invalid or unsupported start parameter.")



# from aiogram import Dispatcher

# dp = Dispatcher()
# dp.message.middleware(StartParamMiddleware([SomeData, OtherData], {
#     SomeData: handle_some,
#     OtherData: handle_other,
# }))
