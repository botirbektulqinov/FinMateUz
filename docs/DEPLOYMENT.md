# Production Deployment

Target:

- Root domain redirects to the dashboard domain.
- Dashboard: `https://app.finmates.app`
- API: `https://api.finmates.app`
- Server: Ubuntu VPS
- Reverse proxy: Caddy installed directly on the server
- Runtime: Docker Compose production stack

This repository intentionally does not store the server IP, real secrets, or a server Caddyfile. Keep those values on the server or in the DNS/control-panel configuration.

## DNS

In your DNS provider, point the required host records to the production server:

```text
A @   -> <server-ip>
A www -> <server-ip>
A app -> <server-ip>
A api -> <server-ip>
```

Wait for DNS propagation before expecting Caddy certificates to issue.

## Firewall

Only SSH, HTTP, and HTTPS should be publicly reachable:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
sudo ufw status
```

Do not expose ports `3000`, `8000`, `5432`, or `6379` publicly. Production Docker Compose binds web/API to `127.0.0.1`; PostgreSQL and Redis have no public port mapping.

## Ubuntu Setup

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y git curl ca-certificates gnupg
```

Install Docker using Docker's official Ubuntu instructions, then verify:

```bash
docker --version
docker compose version
```

If needed, add your deploy user to the Docker group:

```bash
sudo usermod -aG docker "$USER"
```

Log out and back in after changing Docker group membership.

## Caddy

Caddy is managed directly on the server, outside this repository. The server Caddyfile should:

- redirect the root domain and `www` host to `https://app.finmates.app`
- reverse proxy `app.finmates.app` to `127.0.0.1:3000`
- reverse proxy `api.finmates.app` to `127.0.0.1:8000`

Validate and reload after editing the server Caddyfile:

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
sudo systemctl status caddy
```

Caddy automatically issues and renews HTTPS certificates.

## Clone

```bash
cd /opt
git clone https://github.com/botirbektulqinov/FinMateUz.git finmateuz
cd /opt/finmateuz
```

If cloned with `sudo`, fix ownership:

```bash
sudo chown -R "$USER":"$USER" /opt/finmateuz
```

## Environment

Create `.env` on the server and fill production values manually:

```bash
cp .env.example .env
nano .env
```

Required production values:

```text
ENVIRONMENT=production
POSTGRES_DB=finmate
POSTGRES_USER=finmate
POSTGRES_PASSWORD=<strong-postgres-password>
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg://finmate:<strong-postgres-password>@postgres:5432/finmate
REDIS_URL=redis://redis:6379/0
JWT_SECRET_KEY=<long-random-secret>
CORS_ORIGINS=["https://app.finmates.app","https://finmates.app","https://www.finmates.app"]
TELEGRAM_BOT_TOKEN=<botfather-token>
API_BASE_URL=https://api.finmates.app/api/v1
BOT_API_TOKEN=<strong-internal-token>
NEXT_PUBLIC_API_URL=https://api.finmates.app/api/v1
```

Never commit `.env`.

## Start

```bash
docker compose -f docker-compose.prod.yml up --build -d
docker compose -f docker-compose.prod.yml ps
```

The API command runs Alembic migrations before starting Uvicorn.

## Logs

```bash
docker compose -f docker-compose.prod.yml logs -f api
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml logs -f bot
```

## Health Checks

```bash
curl http://127.0.0.1:8000/health
curl -I http://127.0.0.1:3000
curl -I https://api.finmates.app/health
curl -I https://app.finmates.app
curl -I https://finmates.app
curl -I https://www.finmates.app
```

Expected:

- API local health returns `{"status":"ok"}`.
- `https://api.finmates.app/health` returns HTTP 200.
- `https://app.finmates.app` returns dashboard HTML.
- root and `www` redirect to the dashboard domain.

## Deploy Updates

From `/opt/finmateuz`:

```bash
bash scripts/deploy-production.sh
```

Equivalent manual commands:

```bash
git pull --ff-only
docker compose -f docker-compose.prod.yml up --build -d
docker compose -f docker-compose.prod.yml ps
curl -f http://127.0.0.1:8000/health
curl -I http://127.0.0.1:3000
```

## PostgreSQL Backups

At minimum, schedule regular logical dumps and store them off-server:

```bash
docker compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U finmate -d finmate > "finmate-$(date +%F).sql"
```

For real production usage, also enable provider snapshots or move PostgreSQL to a managed database with automated backups and restore testing.

## Troubleshooting

### Caddy 502

Check containers:

```bash
docker compose -f docker-compose.prod.yml ps
```

Check logs:

```bash
docker compose -f docker-compose.prod.yml logs --tail=120 api
docker compose -f docker-compose.prod.yml logs --tail=120 web
docker compose -f docker-compose.prod.yml logs --tail=120 bot
```

Check local listeners:

```bash
ss -lntp | grep ':3000\|:8000'
```

Verify environment:

```bash
grep -E 'DATABASE_URL|REDIS_URL|NEXT_PUBLIC_API_URL|API_BASE_URL|CORS_ORIGINS' .env
```

Common causes:

- `DATABASE_URL` uses `localhost` instead of `postgres`.
- `REDIS_URL` uses `localhost` instead of `redis`.
- API failed startup because production secrets still use placeholders.
- Web was built without `NEXT_PUBLIC_API_URL=https://api.finmates.app/api/v1`.
- Caddy loaded an old config or DNS does not point to the current server.
