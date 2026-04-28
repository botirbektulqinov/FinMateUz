from dataclasses import dataclass
from typing import Protocol

from httpx import AsyncClient, HTTPStatusError

from bot.config import get_settings


@dataclass(frozen=True)
class LinkedTelegramUser:
    telegram_user_id: int
    access_token: str
    company_id: str
    user_id: str
    role: str


@dataclass(frozen=True)
class CategoryOption:
    id: str
    name: str
    type: str


class BackendGateway(Protocol):
    async def get_linked_user(self, telegram_user_id: int) -> LinkedTelegramUser | None:
        ...

    async def link_telegram_user(self, telegram_user_id: int, link_code: str) -> bool:
        ...

    async def list_categories(self, user: LinkedTelegramUser, tx_type: str | None = None) -> list[CategoryOption]:
        ...

    async def create_transaction(self, user: LinkedTelegramUser, payload: dict) -> dict:
        ...

    async def update_transaction(self, user: LinkedTelegramUser, transaction_id: str, payload: dict) -> dict:
        ...

    async def delete_transaction(self, user: LinkedTelegramUser, transaction_id: str) -> None:
        ...

    async def overview_report(self, user: LinkedTelegramUser) -> dict:
        ...

    async def category_breakdown(self, user: LinkedTelegramUser, tx_type: str, category_name: str | None = None) -> list[dict]:
        ...

    async def get_last_transaction(self, user: LinkedTelegramUser) -> dict | None:
        ...


class HttpBackendGateway:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or get_settings().api_base_url

    def _headers(self, user: LinkedTelegramUser) -> dict[str, str]:
        return {"Authorization": f"Bearer {user.access_token}", "X-Company-Id": user.company_id}

    def _bot_headers(self) -> dict[str, str]:
        return {"X-Bot-Api-Token": get_settings().bot_api_token}

    async def get_linked_user(self, telegram_user_id: int) -> LinkedTelegramUser | None:
        async with AsyncClient(base_url=self.base_url, timeout=10) as client:
            try:
                response = await client.get(f"/bot/telegram-accounts/{telegram_user_id}", headers=self._bot_headers())
                if response.status_code == 404:
                    return None
                response.raise_for_status()
            except HTTPStatusError:
                raise
            data = response.json()
            return LinkedTelegramUser(
                telegram_user_id=telegram_user_id,
                access_token=data["access_token"],
                company_id=data["company_id"],
                user_id=data["user_id"],
                role=data["role"],
            )

    async def link_telegram_user(self, telegram_user_id: int, link_code: str) -> bool:
        async with AsyncClient(base_url=self.base_url, timeout=10) as client:
            response = await client.post(
                "/bot/link",
                json={"telegram_user_id": telegram_user_id, "link_code": link_code},
                headers=self._bot_headers(),
            )
            response.raise_for_status()
            return bool(response.json().get("linked"))

    async def list_categories(self, user: LinkedTelegramUser, tx_type: str | None = None) -> list[CategoryOption]:
        params = {"type": tx_type} if tx_type else None
        async with AsyncClient(base_url=self.base_url, timeout=10) as client:
            response = await client.get("/categories", params=params, headers=self._headers(user))
            response.raise_for_status()
            return [CategoryOption(id=item["id"], name=item["name"], type=item["type"]) for item in response.json()]

    async def create_transaction(self, user: LinkedTelegramUser, payload: dict) -> dict:
        async with AsyncClient(base_url=self.base_url, timeout=10) as client:
            response = await client.post("/transactions", json=payload, headers=self._headers(user))
            response.raise_for_status()
            return response.json()

    async def update_transaction(self, user: LinkedTelegramUser, transaction_id: str, payload: dict) -> dict:
        async with AsyncClient(base_url=self.base_url, timeout=10) as client:
            response = await client.patch(f"/transactions/{transaction_id}", json=payload, headers=self._headers(user))
            response.raise_for_status()
            return response.json()

    async def delete_transaction(self, user: LinkedTelegramUser, transaction_id: str) -> None:
        async with AsyncClient(base_url=self.base_url, timeout=10) as client:
            response = await client.delete(f"/transactions/{transaction_id}", headers=self._headers(user))
            response.raise_for_status()

    async def overview_report(self, user: LinkedTelegramUser) -> dict:
        async with AsyncClient(base_url=self.base_url, timeout=10) as client:
            response = await client.get("/reports/overview", headers=self._headers(user))
            response.raise_for_status()
            return response.json()

    async def category_breakdown(self, user: LinkedTelegramUser, tx_type: str, category_name: str | None = None) -> list[dict]:
        async with AsyncClient(base_url=self.base_url, timeout=10) as client:
            response = await client.get("/reports/category-breakdown", params={"type": tx_type}, headers=self._headers(user))
            response.raise_for_status()
            rows = response.json()
            if category_name:
                return [row for row in rows if row["category_name"].lower() == category_name.lower()]
            return rows

    async def get_last_transaction(self, user: LinkedTelegramUser) -> dict | None:
        async with AsyncClient(base_url=self.base_url, timeout=10) as client:
            response = await client.get("/transactions/recent", headers=self._headers(user))
            response.raise_for_status()
            rows = response.json()
            return rows[0] if rows else None
