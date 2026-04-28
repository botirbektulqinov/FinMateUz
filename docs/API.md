# API

Base URL: `/api/v1`

Company-scoped endpoints require:

- `Authorization: Bearer <access_token>`
- `X-Company-Id: <company_id>`

All company-scoped service queries filter by `company_id`.

## Auth

| Method | Path | Description |
| --- | --- | --- |
| POST | `/auth/register` | Create user, company, owner membership, default categories |
| POST | `/auth/login` | Return access/refresh tokens |
| POST | `/auth/refresh` | Exchange refresh token for a new token pair |
| GET | `/auth/me` | Current user profile |

Register:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"owner@example.com","full_name":"Owner","password":"Password123","company_name":"Company LLC","business_type":"Retail"}'
```

## Companies

| Method | Path | Access |
| --- | --- | --- |
| POST | `/companies` | authenticated user |
| GET | `/companies/current` | company member |
| PATCH | `/companies/current` | owner, manager |
| GET | `/companies/me` | authenticated user |
| GET | `/companies/members` | company member |

## Categories

| Method | Path | Access |
| --- | --- | --- |
| GET | `/categories?type=income\|expense` | company member |
| POST | `/categories` | owner, manager |
| PATCH | `/categories/{category_id}` | owner, manager |
| DELETE | `/categories/{category_id}` | owner, manager |

Used categories are soft-deleted; unused categories may be hard-deleted.

## Transactions

| Method | Path | Access |
| --- | --- | --- |
| GET | `/transactions` | company member |
| POST | `/transactions` | owner, manager, accountant, operator |
| PATCH | `/transactions/{transaction_id}` | owner, manager, accountant; operator only own pending |
| DELETE | `/transactions/{transaction_id}` | owner, manager, accountant; operator only own pending by default |
| POST | `/transactions/{transaction_id}/approve` | owner, manager, accountant |
| POST | `/transactions/{transaction_id}/reject` | owner, manager, accountant |
| GET | `/transactions/recent` | company member |

Filters:

- `start_date`
- `end_date`
- `type`
- `category_id`
- `status`
- `search`
- `limit`
- `offset`

Create:

```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "X-Company-Id: $COMPANY_ID" \
  -H "Content-Type: application/json" \
  -d '{"type":"expense","amount":"250000","currency":"UZS","category_id":"<category_id>","transaction_date":"2026-04-27","note":"Delivery","source":"dashboard"}'
```

Business rules:

- Amount must be positive.
- Category must belong to the selected company.
- Category type must match transaction type.
- Operators create `pending` transactions.
- Owner/manager/accountant create `confirmed` transactions.
- `deleted` transactions are excluded from normal lists and reports.

## Reports

| Method | Path | Description |
| --- | --- | --- |
| GET | `/reports/overview` | Current month income/expense/net and recent transactions |
| GET | `/reports/cash-flow` | Time series for income/expense/net |
| GET | `/reports/category-breakdown?type=income\|expense` | Category totals |
| GET | `/reports/top-categories?type=income\|expense` | Highest category totals |
| GET | `/reports/dashboard` | Combined dashboard payload |

Reports use confirmed transactions by default. Add `include_pending=true` where supported to include pending operator submissions.

## Audit Logs

| Method | Path | Access |
| --- | --- | --- |
| GET | `/audit-logs` | company member |

Audit log records are company-scoped.

## Telegram Bot Linking

| Method | Path | Access |
| --- | --- | --- |
| GET | `/bot/link-code` | company member |
| POST | `/bot/link` | bot service with `X-Bot-Api-Token` |
| GET | `/bot/telegram-accounts/{telegram_user_id}` | bot service with `X-Bot-Api-Token` |

Dashboard users generate a short-lived link command in Settings and send it to the Telegram bot:

```text
/link <code>
```

The bot uses the linked account to make company-scoped API calls.

## Error Shape

FastAPI validation errors use the standard `detail` array. Business-rule errors return:

```json
{ "detail": "Category type does not match transaction" }
```
