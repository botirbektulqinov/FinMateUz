from bot.parsers import ParsedMessage, parse_message


def reply_for_parsed(parsed: ParsedMessage) -> str:
    if parsed.intent == "get_report":
        return "Hisobotni tayyorlayapman. Bir necha soniya kuting."
    if parsed.intent == "delete_last_transaction":
        return "Oxirgi tranzaksiyani o'chirish uchun tasdiq kerak. O'chiraymi?"
    if parsed.intent == "edit_last_transaction":
        return "Oxirgi tranzaksiya summasini yangilash uchun tasdiqlayman."
    if parsed.intent not in {"create_income", "create_expense"}:
        return "Tushunmadim. Masalan: bugun 250 ming logistika uchun ketdi."
    if "amount" in parsed.missing_fields:
        return "Summani yozing, iltimos. Masalan: 250 ming."
    if "type" in parsed.missing_fields:
        return "Bu kirimmi yoki xarajatmi?"
    if "category" in parsed.missing_fields:
        return "Qaysi kategoriya? Masalan: logistika, ijara, savdo yoki xizmat."
    if parsed.confidence < 0.70:
        return "To'g'ri tushundimmi? Tranzaksiyani saqlashdan oldin tasdiqlang."
    direction = "kirim" if parsed.type == "income" else "xarajat"
    pending_hint = " Agar rolingiz operator bo'lsa, tranzaksiya tasdiq kutadi."
    amount = parsed.amount.value if parsed.amount else 0
    return f"{amount:,.0f} UZS {direction} sifatida saqlashga tayyor. Sana: {parsed.transaction_date.isoformat()}.{pending_hint}"


def handle_text(text: str) -> str:
    return reply_for_parsed(parse_message(text))
