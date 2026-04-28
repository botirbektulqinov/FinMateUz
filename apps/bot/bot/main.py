import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.config import get_settings
from bot.handlers import build_message_router
from bot.services.factory import create_conversation_service, create_transcriber


async def main() -> None:
    settings = get_settings()
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()
    dp.include_router(build_message_router(create_conversation_service(), create_transcriber()))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
