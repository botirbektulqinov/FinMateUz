from dataclasses import dataclass
from decimal import Decimal

from bot.parsers.models import ParsedMessage, TransactionType


@dataclass
class PendingTransactionDraft:
    parsed: ParsedMessage
    telegram_user_id: int


@dataclass
class ConversationState:
    pending_draft: PendingTransactionDraft | None = None


class ConversationStore:
    def get(self, telegram_user_id: int) -> ConversationState:
        raise NotImplementedError

    def set(self, telegram_user_id: int, state: ConversationState) -> None:
        raise NotImplementedError

    def clear(self, telegram_user_id: int) -> None:
        raise NotImplementedError


class InMemoryConversationStore(ConversationStore):
    def __init__(self) -> None:
        self._states: dict[int, ConversationState] = {}

    def get(self, telegram_user_id: int) -> ConversationState:
        return self._states.setdefault(telegram_user_id, ConversationState())

    def set(self, telegram_user_id: int, state: ConversationState) -> None:
        self._states[telegram_user_id] = state

    def clear(self, telegram_user_id: int) -> None:
        self._states.pop(telegram_user_id, None)
