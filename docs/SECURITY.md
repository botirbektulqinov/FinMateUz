# Security

## Threat Model

FinMate UZ protects small-business finance data. The main threats are cross-company data access, unauthorized financial changes, incorrect report inclusion, leaked secrets, and Telegram users acting before account linking.

## Auth Model

- API users authenticate with JWT access/refresh tokens.
- Company-scoped endpoints require `X-Company-Id`.
- `get_company_context` verifies that the authenticated user is a member of that company.
- Bot users must be linked to an application user/company before any backend company call.

## RBAC Matrix

| Capability | Owner | Manager | Accountant | Operator | Viewer |
| --- | --- | --- | --- | --- | --- |
| Read transactions/reports/categories | yes | yes | yes | yes | yes |
| Create transaction | confirmed | confirmed | confirmed | pending | no |
| Edit any transaction | yes | yes | yes | no | no |
| Edit own pending transaction | yes | yes | yes | yes | no |
| Delete confirmed transaction | yes | yes | yes | no by default | no |
| Delete own pending transaction | yes | yes | yes | yes | no |
| Approve/reject transaction | yes | yes | yes | no | no |
| Manage categories | yes | yes | no | no | no |
| Manage members | yes | yes | no | no | no |

## Company Isolation

Services scope every category, transaction, report, and audit query by `ctx.company_id`. Cross-company headers are rejected before service execution. Tests cover isolation for transactions and reports.

## Financial Record Rules

- Amount must be positive.
- Category type must match transaction type.
- Deleted records use `status=deleted` and `deleted_at`.
- Reports include `confirmed` only by default.
- `include_pending=true` is explicit and used only where supported.

## Audit Logs

Audit logs are written for transaction create/update/delete/approve/reject and category create/update/delete. Login audit is recorded when a membership can be resolved.

## Error Handling

The API hides stack traces outside local development. User-facing web and bot errors avoid internal details.

## Known Limitations

- Stateless refresh tokens cannot be revoked yet.
- Telegram account linking uses short-lived signed codes, but there is no link-management UI for revoking a Telegram account yet.
- Rate limiting is not implemented.
- Production webhook hardening is documented but not fully implemented.
