Create an AGENTS.md file at the repository root for this project.

Project name: FinMate UZ

FinMate UZ is a Telegram-first cash flow management SaaS for small and medium businesses in Uzbekistan. Teams can log income and expenses through a Telegram bot using text or voice, and business owners can monitor finances through a polished web dashboard.

You are working as a strong middle-level fullstack/backend engineer. Prioritize clean architecture, maintainability, security, testability, and product quality.

General engineering rules:
- Use clear modular architecture.
- Avoid overengineering, but do not write toy code.
- Prefer explicit, readable code over clever abstractions.
- Every feature must be implemented in a production-like way.
- Do not leave TODO-only placeholders for core business logic.
- Add meaningful error handling.
- Add validation at API and database boundaries.
- Keep business logic separate from framework-specific code where possible.
- Write tests for critical financial and permission logic.
- Keep README and .env.example updated when adding new services or configuration.
- Never commit real secrets, tokens, API keys, or credentials.
- Use English for code, comments, commits, docs, and API names.
- The product UX copy may support Uzbek Latin.

Security rules:
- Company data must be strictly isolated by company_id.
- A user must never access another company’s transactions, categories, reports, or audit logs.
- Implement role-based access control.
- Use soft delete for financial records.
- Record audit logs for create/update/delete operations on transactions and categories.
- Validate amount, type, date, category, and ownership.
- Sanitize and validate all user-generated text.
- Do not expose stack traces to API clients.

Testing rules:
- Add backend unit/integration tests for financial calculations, transaction CRUD, filters, company isolation, RBAC, and report calculations.
- Add bot handler/parser tests for common Uzbek/Russian/English-style transaction inputs.
- Add frontend tests only where practical, but keep UI components structured for testability.
- All tests should be runnable locally.

Preferred stack:
- Backend API: Python, FastAPI, SQLAlchemy 2.x, Alembic, PostgreSQL, Pydantic.
- Telegram Bot: aiogram 3.x.
- Background jobs/cache: Redis, Celery or RQ if needed.
- Frontend: Next.js, TypeScript, Tailwind CSS, TanStack Query, Recharts.
- Infra: Docker Compose for local development.
- Testing: pytest, pytest-asyncio, httpx TestClient or equivalent, Playwright if feasible.
- Auth: JWT access/refresh token or secure session-based auth.
- Database: PostgreSQL.
- Currency default: UZS.

Product principles:
- This is not a generic admin dashboard.
- The dashboard must feel like a trustworthy finance product for real Uzbek businesses.
- Empty states must guide users.
- Bot messages must feel natural, clear, and helpful.
- If user input is ambiguous, ask a follow-up instead of silently saving wrong data.
- Every transaction should have amount, type, category, date, optional note, source, creator, and status.
- Data from Telegram bot and dashboard must stay in sync through the same backend API/database.

When implementing:
1. First inspect the existing repository.
2. Explain the plan briefly.
3. Make focused changes.
4. Run available tests/lint/build commands.
5. Summarize what changed and what remains.