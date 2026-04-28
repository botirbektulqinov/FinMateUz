from dataclasses import dataclass
from httpx import AsyncClient

from bot.config import get_settings
from bot.parsers import ParsedMessage


@dataclass(frozen=True)
class BotUserContext:
    access_token: str
    company_id: str


class BackendClient:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or get_settings().api_base_url

    async def create_transaction(self, ctx: BotUserContext, parsed: ParsedMessage, category_id: str) -> dict:
        payload = {
            "type": parsed.type,
            "amount": str(parsed.amount.value if parsed.amount else ""),
            "currency": parsed.amount.currency if parsed.amount else "UZS",
            "category_id": category_id,
            "transaction_date": parsed.transaction_date.isoformat() if parsed.transaction_date else None,
            "note": parsed.note,
            "source": "telegram",
            "raw_text": parsed.note,
            "confidence_score": str(parsed.confidence),
        }
        async with AsyncClient(base_url=self.base_url, timeout=10) as client:
            response = await client.post(
                "/transactions",
                json=payload,
                headers={"Authorization": f"Bearer {ctx.access_token}", "X-Company-Id": ctx.company_id},
            )
            response.raise_for_status()
            return response.json()

    async def dashboard_report(self, ctx: BotUserContext) -> dict:
        async with AsyncClient(base_url=self.base_url, timeout=10) as client:
            response = await client.get(
                "/reports/dashboard",
                headers={"Authorization": f"Bearer {ctx.access_token}", "X-Company-Id": ctx.company_id},
            )
            response.raise_for_status()
            return response.json()
