from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.services.conversation import BotConversationService
from bot.services.transcribers import BaseTranscriber


def build_message_router(conversation: BotConversationService, transcriber: BaseTranscriber) -> Router:
    router = Router()

    @router.message(CommandStart())
    async def start(message: Message) -> None:
        await message.answer(
            "Assalomu alaykum! FinMate UZ tayyor.\n"
            "Kirim yoki chiqimni oddiy yozing: bugun 250 ming logistika uchun ketdi."
        )

    @router.message(F.text)
    async def text_message(message: Message) -> None:
        telegram_user_id = message.from_user.id if message.from_user else 0
        reply = await conversation.handle_text(telegram_user_id, message.text or "")
        await message.answer(reply)

    @router.message(F.voice)
    async def voice_message(message: Message) -> None:
        telegram_user_id = message.from_user.id if message.from_user else 0
        file_path = f"telegram-voice-{message.voice.file_id if message.voice else 'unknown'}.ogg"
        text = await transcriber.transcribe(file_path)
        reply = await conversation.handle_text(telegram_user_id, text)
        await message.answer(reply)

    return router
