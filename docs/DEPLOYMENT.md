# Deployment

## Backend

- Deploy `apps/api` as a Python 3.12+ service.
- Set `ENVIRONMENT=production`.
- Use a strong `JWT_SECRET_KEY` from a secret manager.
- Set `DATABASE_URL` to a managed PostgreSQL instance.
- Set `REDIS_URL` to a managed Redis instance if bot sessions/cache move there.
- Run `alembic upgrade head` before or during deploy.
- Expose `/health` for platform health checks.

Recommended process:

```bash
cd apps/api
pip install .
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Docker Compose production-style deployment is also available:

```bash
cp .env.production.example .env
# replace every secret and domain in .env
docker compose -f docker-compose.prod.yml up --build -d
```

## Frontend

- Deploy `apps/web` as a Next.js app.
- Set `NEXT_PUBLIC_API_URL` to the public API base URL.
- Run `npm ci`, `npm run build`, then start with `npm run start`. `npm run dev` is local-only.

## Database

- Use PostgreSQL 16+.
- Enable automated backups and point-in-time recovery.
- Restrict network access to the API runtime.
- Run migrations from a controlled deploy job.

## Redis

Redis is included for future cache/session/background needs. In production, use authenticated managed Redis and avoid public exposure.

## Telegram Bot

Local development uses polling. Production can use either:

- Polling worker: simple deployment, one active instance.
- Webhook: set `TELEGRAM_WEBHOOK_URL`, terminate TLS at the platform/load balancer, and route Telegram updates to the bot service.

The bot must resolve Telegram users to linked application users before making company-scoped API calls.

## Environment Variables

See `.env.example`. Production values should come from secret management, not repository files.

Minimum production set:

- `ENVIRONMENT`
- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET_KEY`
- `CORS_ORIGINS`
- `TELEGRAM_BOT_TOKEN`
- `API_BASE_URL`
- `NEXT_PUBLIC_API_URL`
- `BOT_API_TOKEN`

## CI/CD

GitHub Actions run API tests, bot tests, web lint/typecheck/tests/build, and Docker Compose config validation on pull requests and pushes to `main`.

Production deployment is intentionally gated:

- Set repository variable `PRODUCTION_DEPLOY_ENABLED=true`.
- Configure `PRODUCTION_HOST`, `PRODUCTION_USER`, and `PRODUCTION_SSH_KEY`.
- Keep production `.env` on the server, outside Git.
- The deploy workflow fetches `main`, rebuilds Docker Compose services, and runs migrations.

## Operational Notes

- Monitor API 5xx rates and slow requests.
- Monitor failed login volume.
- Track pending approval count per company.
- Confirm backup restore procedure before real usage.
