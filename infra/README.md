# FinMate UZ Infrastructure

Local development uses Docker Compose with PostgreSQL 16, Redis 7, the FastAPI API, the optional Telegram bot service, and the Next.js web app.

Run core services:

```bash
cp .env.example .env
make up
```

Run the bot after setting `TELEGRAM_BOT_TOKEN`:

```bash
docker compose --profile bot up bot
```

Health checks:

- API: `http://localhost:8000/health`
- Web: `http://localhost:3000`

Operational commands:

```bash
make migrate
make seed
make checks
```
