from dataclasses import replace
from decimal import Decimal

from httpx import HTTPError

from bot.parsers import Intent, ParsedMessage, ReportKind, TransactionType, parse_amount, parse_message
from bot.parsers.categories import infer_category
from bot.parsers.text import normalize
from bot.services.backend import BackendGateway, CategoryOption, LinkedTelegramUser
from bot.states.conversation import ConversationState, ConversationStore, PendingTransactionDraft


def format_money(value: str | int | Decimal, currency: str = "UZS") -> str:
    amount = Decimal(str(value))
    formatted = f"{amount:,.0f}".replace(",", " ")
    suffix = "so‘m" if currency == "UZS" else currency
    return f"{formatted} {suffix}"


class BotConversationService:
    def __init__(self, backend: BackendGateway, store: ConversationStore) -> None:
        self.backend = backend
        self.store = store

    async def handle_text(self, telegram_user_id: int, text: str) -> str:
        if text.strip().lower().startswith("/link"):
            return await self._handle_link_command(telegram_user_id, text)
        user = await self.backend.get_linked_user(telegram_user_id)
        if not user:
            return (
                "FinMate UZ hisobingiz Telegramga ulanmagan.\n"
                "Dashboardga kiring, Settings → Telegram bo‘limidan ulash kodini oling va /link <kod> yuboring."
            )
        try:
            state = self.store.get(telegram_user_id)
            if state.pending_draft:
                return await self._handle_follow_up(user, state.pending_draft, text)
            parsed = parse_message(text)
            return await self._dispatch(user, parsed)
        except HTTPError:
            return "Backend bilan aloqa vaqtincha ishlamadi. Birozdan keyin qayta urinib ko‘ring."
        except Exception:
            return "Kutilmagan xatolik bo‘ldi. Xabarni soddaroq yozib qayta yuboring."

    async def _handle_link_command(self, telegram_user_id: int, text: str) -> str:
        parts = text.strip().split(maxsplit=1)
        if len(parts) != 2 or not parts[1].strip():
            return "Ulash kodi yetishmayapti. Dashboard Settings bo‘limidan kod olib, /link <kod> ko‘rinishida yuboring."
        try:
            linked = await self.backend.link_telegram_user(telegram_user_id, parts[1].strip())
        except HTTPError:
            return "Ulash kodi noto‘g‘ri yoki muddati tugagan. Dashboarddan yangi kod olib qayta urinib ko‘ring."
        if linked:
            self.store.clear(telegram_user_id)
            return "Telegram hisobingiz FinMate UZ bilan ulandi ✅ Endi kirim yoki chiqimni oddiy yozishingiz mumkin."
        return "Telegram hisobini ulab bo‘lmadi. Dashboarddan yangi kod olib qayta urinib ko‘ring."

    async def _dispatch(self, user: LinkedTelegramUser, parsed: ParsedMessage) -> str:
        if parsed.intent in {Intent.create_income, Intent.create_expense}:
            return await self._handle_create_transaction(user, parsed)
        if parsed.intent == Intent.get_report:
            return await self._handle_report(user, parsed)
        if parsed.intent == Intent.delete_last_transaction:
            return await self._delete_last_transaction(user)
        if parsed.intent == Intent.edit_last_transaction:
            return await self._edit_last_transaction(user, parsed)
        if parsed.intent == Intent.create_category:
            return "Kategoriya yaratish dashboard orqali tasdiqlanadi. Hozircha Settings → Categories bo‘limidan qo‘shing."
        if parsed.intent == Intent.ask_question:
            return "Savolingizni hisobot yoki transaction shaklida yozing. Masalan: bu oy qancha xarajat qildik?"
        return "Tushunmadim. Masalan: bugun 250 ming logistika uchun ketdi."

    async def _handle_create_transaction(self, user: LinkedTelegramUser, parsed: ParsedMessage) -> str:
        if "amount" in parsed.missing_fields:
            self._save_draft(user.telegram_user_id, parsed)
            return "Summani yozing, iltimos. Masalan: 250 ming yoki 1.2 mln."
        if "type" in parsed.missing_fields:
            self._save_draft(user.telegram_user_id, parsed)
            return "Bu kirimmi yoki chiqimmi? Masalan: “kirim” yoki “chiqim” deb yozing."
        if "category" in parsed.missing_fields:
            self._save_draft(user.telegram_user_id, parsed)
            categories = await self.backend.list_categories(user, parsed.type.value if parsed.type else None)
            names = ", ".join(category.name for category in categories[:5])
            amount_text = format_money(parsed.amount.value, parsed.amount.currency) if parsed.amount else "Shu summa"
            direction = "chiqim" if parsed.type == TransactionType.expense else "kirim"
            return f"{amount_text} {direction} ekanligini tushundim. Qaysi kategoriya bo‘yicha yozay? {names}"
        if parsed.needs_confirmation:
            self._save_draft(user.telegram_user_id, parsed)
            return "To‘g‘ri tushundimmi? Saqlashdan oldin tasdiqlang: Ha deb yozing yoki Bekor deb yuboring."
        return await self._save_transaction(user, parsed)

    async def _handle_follow_up(self, user: LinkedTelegramUser, draft: PendingTransactionDraft, text: str) -> str:
        normalized = text.strip().lower()
        if normalized in {"ha", "xa", "tasdiq", "tasdiqlayman"} and not draft.parsed.missing_fields:
            self.store.clear(user.telegram_user_id)
            return await self._save_transaction(user, draft.parsed)
        if normalized in {"bekor", "yo'q", "yo‘q"}:
            self.store.clear(user.telegram_user_id)
            return "Bekor qilindi. Transaction saqlanmadi."
        parsed_follow_up = parse_message(text)
        merged = self._merge_draft(draft.parsed, parsed_follow_up, text)
        if "category" in merged.missing_fields and merged.type:
            merged = await self._merge_category_choice(user, merged, text)
        self.store.clear(user.telegram_user_id)
        return await self._handle_create_transaction(user, merged)

    def _merge_draft(self, draft: ParsedMessage, follow_up: ParsedMessage, raw_follow_up: str) -> ParsedMessage:
        amount = follow_up.amount or draft.amount
        tx_type = follow_up.type or draft.type
        category_key = follow_up.category_key or draft.category_key
        category_name = follow_up.category_name or draft.category_name
        if not category_name:
            key, name, _ = infer_category(raw_follow_up, tx_type)
            category_key = key or category_key
            category_name = name or category_name
        missing = []
        if amount is None:
            missing.append("amount")
        if tx_type is None:
            missing.append("type")
        if category_name is None:
            missing.append("category")
        return replace(
            draft,
            amount=amount,
            type=tx_type,
            category_key=category_key,
            category_name=category_name,
            note=draft.note or follow_up.note,
            missing_fields=missing,
            confidence=max(draft.confidence, follow_up.confidence),
            needs_confirmation=False if not missing else draft.needs_confirmation,
        )

    async def _merge_category_choice(self, user: LinkedTelegramUser, parsed: ParsedMessage, raw_follow_up: str) -> ParsedMessage:
        categories = await self.backend.list_categories(user, parsed.type.value)
        normalized = normalize(raw_follow_up)
        for category in categories:
            category_name = normalize(category.name)
            if normalized == category_name or normalized in category_name or category_name in normalized:
                missing = [field for field in parsed.missing_fields if field != "category"]
                return replace(parsed, category_name=category.name, category_key=category.id, missing_fields=missing, needs_confirmation=False)
        return parsed

    async def _save_transaction(self, user: LinkedTelegramUser, parsed: ParsedMessage) -> str:
        category = await self._resolve_category(user, parsed)
        if not category:
            self._save_draft(user.telegram_user_id, parsed)
            return "Qaysi kategoriya bo‘yicha yozay? Kategoriyani nomi bilan yuboring."
        payload = {
            "type": parsed.type.value if parsed.type else None,
            "amount": str(parsed.amount.value if parsed.amount else ""),
            "currency": parsed.amount.currency if parsed.amount else "UZS",
            "category_id": category.id,
            "transaction_date": (parsed.transaction_date).isoformat() if parsed.transaction_date else None,
            "note": parsed.note,
            "source": "telegram",
            "raw_text": parsed.raw_text,
            "confidence_score": str(parsed.confidence),
        }
        saved = await self.backend.create_transaction(user, payload)
        direction = "kirim" if saved["type"] == "income" else "chiqim"
        prefix = "Yozib qo‘ydim ✅"
        if saved.get("status") == "pending":
            prefix = "Tayyor. Bu transaction tasdiqlash uchun yuborildi."
        return f"{prefix}\n{format_money(saved['amount'], saved.get('currency', 'UZS'))} {direction}: {saved.get('category_name') or category.name}."

    async def _resolve_category(self, user: LinkedTelegramUser, parsed: ParsedMessage) -> CategoryOption | None:
        categories = await self.backend.list_categories(user, parsed.type.value if parsed.type else None)
        if parsed.category_name:
            for category in categories:
                if category.name.lower() == parsed.category_name.lower():
                    return category
        return None

    async def _delete_last_transaction(self, user: LinkedTelegramUser) -> str:
        last = await self.backend.get_last_transaction(user)
        if not last:
            return "O‘chirish uchun oxirgi transaction topilmadi."
        await self.backend.delete_transaction(user, last["id"])
        return "Oxirgi transaction o‘chirildi ✅"

    async def _edit_last_transaction(self, user: LinkedTelegramUser, parsed: ParsedMessage) -> str:
        if not parsed.amount:
            return "Yangi summani yozing. Masalan: oxirgisini 90 ming qil."
        last = await self.backend.get_last_transaction(user)
        if not last:
            return "Tahrirlash uchun oxirgi transaction topilmadi."
        updated = await self.backend.update_transaction(user, last["id"], {"amount": str(parsed.amount.value)})
        return f"Tayyor. Oxirgi transaction summasi {format_money(updated['amount'], updated.get('currency', 'UZS'))} qilindi."

    async def _handle_report(self, user: LinkedTelegramUser, parsed: ParsedMessage) -> str:
        if parsed.report_kind == ReportKind.category and parsed.category_name:
            rows = await self.backend.category_breakdown(user, "expense", parsed.category_name)
            total = rows[0]["total"] if rows else "0"
            return f"{parsed.category_name} bo‘yicha bu oy: {format_money(total)}"
        overview = await self.backend.overview_report(user)
        summary = overview["summary"]
        return (
            "Bu oy "
            f"kirim: {format_money(summary['month_income'])}, "
            f"chiqim: {format_money(summary['month_expenses'])}, "
            f"net: {format_money(summary['net_cash_flow'])}"
        )

    def _save_draft(self, telegram_user_id: int, parsed: ParsedMessage) -> None:
        self.store.set(telegram_user_id, ConversationState(PendingTransactionDraft(parsed=parsed, telegram_user_id=telegram_user_id)))
