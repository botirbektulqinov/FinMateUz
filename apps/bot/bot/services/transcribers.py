from abc import ABC, abstractmethod


class BaseTranscriber(ABC):
    @abstractmethod
    async def transcribe(self, file_path: str) -> str:
        raise NotImplementedError


class MockTranscriber(BaseTranscriber):
    def __init__(self, text: str = "bugun 50 ming transport uchun ketdi") -> None:
        self.text = text

    async def transcribe(self, file_path: str) -> str:
        return self.text


class ProviderTranscriber(BaseTranscriber):
    async def transcribe(self, file_path: str) -> str:
        raise RuntimeError("Real speech-to-text provider is not configured for local development")
