from bot.config import get_settings
from bot.services.backend import HttpBackendGateway
from bot.services.conversation import BotConversationService
from bot.services.transcribers import BaseTranscriber, MockTranscriber, ProviderTranscriber
from bot.states.conversation import InMemoryConversationStore


def create_transcriber() -> BaseTranscriber:
    settings = get_settings()
    if settings.transcriber_provider == "mock":
        return MockTranscriber()
    return ProviderTranscriber()


def create_conversation_service() -> BotConversationService:
    return BotConversationService(backend=HttpBackendGateway(), store=InMemoryConversationStore())
