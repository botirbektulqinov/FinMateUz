from decimal import Decimal

from bot.parsers.models import TransactionType
from bot.parsers.text import normalize

CATEGORY_KEYWORDS: dict[str, tuple[str, str, TransactionType]] = {
    "logistika": ("logistics", "Logistics", TransactionType.expense),
    "logistikaga": ("logistics", "Logistics", TransactionType.expense),
    "dostavka": ("logistics", "Logistics", TransactionType.expense),
    "transport": ("transport", "Transport", TransactionType.expense),
    "taxi": ("transport", "Transport", TransactionType.expense),
    "ijara": ("rent", "Rent", TransactionType.expense),
    "arenda": ("rent", "Rent", TransactionType.expense),
    "oylik": ("salary", "Salary", TransactionType.expense),
    "maosh": ("salary", "Salary", TransactionType.expense),
    "internet": ("internet-phone", "Internet and phone", TransactionType.expense),
    "telefon": ("internet-phone", "Internet and phone", TransactionType.expense),
    "phone": ("internet-phone", "Internet and phone", TransactionType.expense),
    "soliq": ("tax", "Tax", TransactionType.expense),
    "ovqat": ("food", "Food", TransactionType.expense),
    "oshxona": ("food", "Food", TransactionType.expense),
    "food": ("food", "Food", TransactionType.expense),
    "marketing": ("marketing", "Marketing", TransactionType.expense),
    "inventory": ("inventory", "Inventory", TransactionType.expense),
    "debt payment": ("debt-payment", "Debt payment", TransactionType.expense),
    "sotuv": ("sales", "Sales", TransactionType.income),
    "sales": ("sales", "Sales", TransactionType.income),
    "savdo": ("sales", "Sales", TransactionType.income),
    "sayt": ("services", "Services", TransactionType.income),
    "xizmat": ("services", "Services", TransactionType.income),
    "services": ("services", "Services", TransactionType.income),
}


def infer_category(text: str, tx_type: TransactionType | None = None) -> tuple[str | None, str | None, Decimal]:
    normalized = normalize(text)
    for keyword, (key, name, category_type) in CATEGORY_KEYWORDS.items():
        if keyword in normalized and (tx_type is None or category_type == tx_type):
            return key, name, Decimal("0.86")
    return None, None, Decimal("0.25")
