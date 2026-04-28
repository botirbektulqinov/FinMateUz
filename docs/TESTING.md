# Testing

## Commands

Root:

```bash
make api-test
make bot-test
make web-test
make web-build
make checks
```

Manual:

```bash
cd apps/api && python -m pytest
cd apps/bot && python -m pytest
cd apps/web && npm run lint && npm run typecheck && npm run test && npm run build
```

## Backend Coverage

The backend suite covers:

- Register/login/refresh/me.
- Company isolation.
- RBAC restrictions.
- Transaction create/update/delete.
- Operator pending transaction behavior.
- Approval flow.
- Category type mismatch rejection.
- Transaction filters.
- Soft delete exclusion.
- Confirmed-only report calculations.
- Optional pending report inclusion.
- Category breakdown calculations.
- Transaction audit log creation.

Tests use SQLite with `StaticPool` for deterministic isolated in-memory runs.

## Bot Coverage

The bot suite covers:

- Amount parsing.
- Date parsing.
- Intent detection.
- Future-date confirmation.
- Ambiguous transaction follow-up.
- Create income/expense flows.
- Delete/edit last transaction flows.
- Report intent flows.
- Unlinked Telegram user flow.

Bot tests use a fake backend gateway so financial business rules are not duplicated.

## Web Coverage

The web suite covers:

- UZS money formatting.
- Helpful empty-state rendering.
- TypeScript compile checks.
- Production build.

Recommended next step: add Playwright smoke tests for login, dashboard overview, transactions approvals, and category management.
