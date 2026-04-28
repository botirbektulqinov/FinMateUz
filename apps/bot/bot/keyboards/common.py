from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def confirmation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Ha", callback_data="confirm:yes"),
                InlineKeyboardButton(text="Tahrirlash", callback_data="confirm:edit"),
                InlineKeyboardButton(text="O‘chirish", callback_data="confirm:delete"),
            ]
        ]
    )


def category_keyboard(categories: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=f"category:{category_id}")]
            for category_id, name in categories[:8]
        ]
    )


def report_shortcuts_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Bu oy", callback_data="report:overview"),
                InlineKeyboardButton(text="Xarajatlar", callback_data="report:expense"),
            ]
        ]
    )


def last_transaction_actions_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Tahrirlash", callback_data="last:edit"),
                InlineKeyboardButton(text="O‘chirish", callback_data="last:delete"),
            ]
        ]
    )
