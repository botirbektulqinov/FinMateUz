# Telegram Bot Flows

The FinMate UZ bot is an aiogram 3.x service for Telegram-first transaction entry and finance questions. It parses Uzbek Latin text or voice transcripts, keeps incomplete input in conversation state, and sends final transaction creation to the backend API so backend validation, RBAC, company isolation, approval flow, and audit behavior remain authoritative.

## Structure

```text
bot/main.py          aiogram app startup
bot/config.py        environment settings
bot/handlers         Telegram message handlers
bot/services         backend gateway, conversation service, transcribers
bot/parsers          amount, date, intent, category, transaction parsers
bot/keyboards        inline keyboard builders
bot/states           conversation state store
bot/tests            pytest parser and flow tests
```

## Linking And Security

Every Telegram user must be linked to an application user/company before company data is shown or changed. If the backend gateway returns no linked account, the bot responds with linking instructions:

```text
FinMate UZ hisobingiz Telegramga ulanmagan.
Dashboardga kiring, Settings → Telegram bo‘limidan ulash kodini oling va /link <kod> yuboring.
```

All backend calls use the linked account token plus `X-Company-Id`, so the bot never queries another company’s data.

## Voice Input

Voice messages use a transcriber adapter:

- `BaseTranscriber`: interface.
- `MockTranscriber`: local development and tests.
- `ProviderTranscriber`: placeholder for a real provider, controlled by `TRANSCRIBER_PROVIDER`.

Local development does not require paid speech-to-text.

## Supported Intents

- `create_income`
- `create_expense`
- `get_report`
- `ask_question`
- `edit_last_transaction`
- `delete_last_transaction`
- `create_category`
- `unknown`

## Example Inputs

- `bugun 250 ming logistika uchun ketdi` → expense, 250000 UZS, Logistics, today.
- `kecha 1 million 200 ming tushdi sayt uchun` → income, 1200000 UZS, Services, yesterday, note `sayt uchun`.
- `50 ming ketdi` → expense, 50000 UZS, missing category, ask follow-up.
- `bu oy qancha xarajat qildik?` → current-month report.
- `logistikaga qancha ketdi?` → Logistics category expense report.
- `oxirgisini o‘chir` → delete last transaction through backend.
- `oxirgisini 90 ming qil` → update last transaction amount through backend.

## Amount Parsing

Supported examples:

- `50000`
- `50 000`
- `50 ming`
- `250 ming`
- `1 mln`
- `1 million`
- `1 million 200 ming`
- `1.2 mln`
- `100 dollar`
- `100 usd`

Default currency is UZS. USD/dollar is detected when explicitly present.

## Date Parsing

Supported:

- `bugun`
- `kecha`
- `ertaga` asks for confirmation because it is a future date.
- `bu hafta`
- `bu oy`
- explicit `YYYY-MM-DD`

## Ambiguity Rules

- Missing amount: ask for the amount.
- Missing type: ask whether it is income or expense.
- Missing category: ask the user to choose/supply a category.
- Missing date: default to today and mention it in confirmation.
- Low confidence: ask confirmation before saving.
- Future date: ask confirmation before saving.
- Unexpected input: return a helpful Uzbek message instead of crashing.

Example:

```text
User: 50 ming ketdi
Bot: 50 000 so‘m chiqim ekanligini tushundim. Qaysi kategoriya bo‘yicha yozay? Logistics, Rent, Transport...
User: logistika
Bot: Tayyor. Bu transaction tasdiqlash uchun yuborildi.
```

## Approval Flow

When the Telegram-linked user has the operator role, created transactions are saved as `pending`. Bot copy must mention that approval is required.

## Keyboards

Inline keyboard builders exist for:

- Confirmation: `Ha`, `Tahrirlash`, `O‘chirish`
- Category choices
- Report shortcuts
- Last transaction actions

## Report Copy

Overview:

```text
Bu oy kirim: 1 200 000 so‘m, chiqim: 250 000 so‘m, net: 950 000 so‘m
```

Category:

```text
Logistics bo‘yicha bu oy: 250 000 so‘m
```

## Screenshot Placeholders

Add screenshots under `docs/screenshots/`:

- `bot-unlinked.png`
- `bot-create-expense-follow-up.png`
- `bot-create-income-confirmed.png`
- `bot-pending-approval.png`
- `bot-report-overview.png`
