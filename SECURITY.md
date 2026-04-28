# Security Policy

This repository is a portfolio MVP, but it models production security decisions for a multi-company finance product.

## Threat Model

Primary risks:

- A user accesses another company’s transactions, categories, reports, members, or audit logs.
- A low-privilege role modifies confirmed financial records.
- Pending or deleted transactions are accidentally counted in final reports.
- Telegram users submit data before linking to an application user/company.
- Secrets are committed or leaked through logs/errors.
- API clients receive stack traces or internal implementation details.

## Auth Model

- API authentication uses JWT access and refresh tokens.
- Company-scoped endpoints also require `X-Company-Id`.
- The backend loads a `MembershipContext` from the authenticated user and selected company.
- Bot calls must resolve the Telegram user to an application user/company before any company data is accessed.

## RBAC Matrix

| Action | Owner | Manager | Accountant | Operator | Viewer |
| --- | --- | --- | --- | --- | --- |
| Read company finance data | yes | yes | yes | yes | yes |
| Create transaction | confirmed | confirmed | confirmed | pending | no |
| Edit any transaction | yes | yes | yes | no | no |
| Edit own pending transaction | yes | yes | yes | yes | no |
| Delete confirmed transaction | yes | yes | yes | no, unless explicitly allowed | no |
| Delete own pending transaction | yes | yes | yes | yes | no |
| Approve/reject pending | yes | yes | yes | no | no |
| Manage categories | yes | yes | no | no | no |
| Manage members | yes | yes | no | no | no |

## Company Isolation

Company isolation is enforced in service/query code using `ctx.company_id`. Routes delegate to services with a membership context. Tests cover cross-company denial and report isolation.

## Audit Logs

Audit logs are recorded for:

- Transaction create/update/delete/approve/reject.
- Category create/update/delete.
- User login where practical.

Audit logs are company-scoped and exposed only through authenticated company context.

## Known Limitations

- Refresh tokens are stateless and are not yet persisted/revoked.
- Telegram account linking endpoint is planned; current bot gateway expects one.
- Local development uses placeholder secrets and should not be reused in production. `ENVIRONMENT=production` validates that key runtime secrets are replaced.
- Fine-grained member management UI is not complete.
- Rate limiting and IP-based abuse protection are not implemented yet.

## Reporting Issues

Do not open public issues with secrets or real customer data. Rotate any exposed token immediately.
