from decimal import Decimal

import pytest

from bot.services.backend import CategoryOption, LinkedTelegramUser
from bot.services.conversation import BotConversationService
from bot.states.conversation import InMemoryConversationStore


class FakeBackend:
    def __init__(self, linked: bool = True) -> None:
        self.user = (
            LinkedTelegramUser(
                telegram_user_id=100,
                access_token="token",
                company_id="company-1",
                user_id="user-1",
                role="operator",
            )
            if linked
            else None
        )
        self.categories = [
            CategoryOption(id="cat-logistics", name="Logistics", type="expense"),
            CategoryOption(id="cat-rent", name="Rent", type="expense"),
            CategoryOption(id="cat-food", name="Food", type="expense"),
            CategoryOption(id="cat-services", name="Services", type="income"),
            CategoryOption(id="cat-sales", name="Sales", type="income"),
        ]
        self.created: list[dict] = []
        self.deleted: list[str] = []
        self.updated: list[tuple[str, dict]] = []
        self.linked_codes: list[str] = []
        self.last_transaction = {
            "id": "tx-1",
            "type": "expense",
            "amount": "50000.00",
            "currency": "UZS",
            "category_name": "Logistics",
            "status": "confirmed",
        }

    async def get_linked_user(self, telegram_user_id: int):
        return self.user

    async def link_telegram_user(self, telegram_user_id: int, link_code: str):
        self.linked_codes.append(link_code)
        return link_code == "valid-code"

    async def list_categories(self, user, tx_type=None):
        return [category for category in self.categories if tx_type is None or category.type == tx_type]

    async def create_transaction(self, user, payload):
        self.created.append(payload)
        return {
            "id": "tx-created",
            "type": payload["type"],
            "amount": Decimal(payload["amount"]),
            "currency": payload["currency"],
            "category_name": "Logistics" if payload["type"] == "expense" else "Services",
            "status": "pending" if user.role == "operator" else "confirmed",
        }

    async def update_transaction(self, user, transaction_id, payload):
        self.updated.append((transaction_id, payload))
        return {
            "id": transaction_id,
            "type": "expense",
            "amount": payload["amount"],
            "currency": "UZS",
            "category_name": "Logistics",
            "status": "confirmed",
        }

    async def delete_transaction(self, user, transaction_id):
        self.deleted.append(transaction_id)

    async def overview_report(self, user):
        return {
            "summary": {
                "month_income": "1200000.00",
                "month_expenses": "250000.00",
                "net_cash_flow": "950000.00",
            }
        }

    async def category_breakdown(self, user, tx_type, category_name=None):
        return [{"category_name": "Logistics", "total": "250000.00"}]

    async def get_last_transaction(self, user):
        return self.last_transaction


@pytest.fixture()
def service_backend():
    backend = FakeBackend()
    service = BotConversationService(backend=backend, store=InMemoryConversationStore())
    return service, backend


@pytest.mark.asyncio
async def test_unlinked_telegram_user_flow() -> None:
    service = BotConversationService(backend=FakeBackend(linked=False), store=InMemoryConversationStore())
    reply = await service.handle_text(100, "bugun 250 ming logistika uchun ketdi")
    assert "Telegramga ulanmagan" in reply


@pytest.mark.asyncio
async def test_link_command_connects_telegram_user() -> None:
    backend = FakeBackend(linked=False)
    service = BotConversationService(backend=backend, store=InMemoryConversationStore())
    reply = await service.handle_text(100, "/link valid-code")
    assert "ulandi" in reply
    assert backend.linked_codes == ["valid-code"]


@pytest.mark.asyncio
async def test_ambiguous_transaction_follow_up(service_backend) -> None:
    service, backend = service_backend
    reply = await service.handle_text(100, "50 ming ketdi")
    assert "Qaysi kategoriya" in reply
    assert backend.created == []


@pytest.mark.asyncio
async def test_create_expense_flow_with_follow_up(service_backend) -> None:
    service, backend = service_backend
    first = await service.handle_text(100, "50 ming ketdi")
    second = await service.handle_text(100, "logistika")
    assert "tasdiqlash uchun yuborildi" in second
    assert backend.created[0]["amount"] == "50000.00"
    assert backend.created[0]["type"] == "expense"
    assert backend.created[0]["category_id"] == "cat-logistics"


@pytest.mark.asyncio
async def test_create_expense_flow_with_english_category_follow_up(service_backend) -> None:
    service, backend = service_backend
    first = await service.handle_text(100, "50 ming ketdi")
    second = await service.handle_text(100, "Food")
    assert "tasdiqlash uchun yuborildi" in second
    assert backend.created[0]["category_id"] == "cat-food"


@pytest.mark.asyncio
async def test_create_income_flow(service_backend) -> None:
    service, backend = service_backend
    reply = await service.handle_text(100, "kecha 1 million 200 ming tushdi sayt uchun")
    assert "Yozib qo‘ydim" in reply or "tasdiqlash uchun yuborildi" in reply
    assert backend.created[0]["amount"] == "1200000.00"
    assert backend.created[0]["type"] == "income"
    assert backend.created[0]["category_id"] == "cat-services"


@pytest.mark.asyncio
async def test_delete_last_transaction_flow(service_backend) -> None:
    service, backend = service_backend
    reply = await service.handle_text(100, "oxirgisini o‘chir")
    assert "o‘chirildi" in reply
    assert backend.deleted == ["tx-1"]


@pytest.mark.asyncio
async def test_edit_last_transaction_amount_flow(service_backend) -> None:
    service, backend = service_backend
    reply = await service.handle_text(100, "oxirgisini 90 ming qil")
    assert "90 000 so‘m" in reply
    assert backend.updated == [("tx-1", {"amount": "90000.00"})]


@pytest.mark.asyncio
async def test_report_intent_flow(service_backend) -> None:
    service, _ = service_backend
    overview = await service.handle_text(100, "bu oy qancha xarajat qildik?")
    category = await service.handle_text(100, "logistikaga qancha ketdi?")
    assert "Bu oy kirim" in overview
    assert "Logistics bo‘yicha bu oy: 250 000 so‘m" == category
