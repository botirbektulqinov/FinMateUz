# Production Deployment

Target:

- Root domain: `https://finmates.app` redirects to `https://app.finmates.app`
- Dashboard: `https://app.finmates.app`
- API: `https://api.finmates.app`
- Server: DigitalOcean Ubuntu VPS, public IP `134.122.92.113`
- Reverse proxy: Caddy installed directly on the server
- Runtime: Docker Compose production stack

## DNS

Create these records at name.com:

```text
A @   -> 134.122.92.113
A www -> 134.122.92.113
A app -> 134.122.92.113
A api -> 134.122.92.113
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

Do not expose ports `3000`, `8000`, `5432`, or `6379` publicly. Docker Compose binds web/API to `127.0.0.1`; PostgreSQL and Redis have no public port mapping.

## Ubuntu Setup

Update the server and install basic tools:

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

Install Caddy using the official Ubuntu package instructions. Then copy the example config:

```bash
sudo mkdir -p /etc/caddy
sudo cp /opt/finmateuz/infra/caddy/Caddyfile.example /etc/caddy/Caddyfile
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
sudo systemctl status caddy
```

Caddyfile:

```caddyfile
finmates.app {
    redir https://app.finmates.app{uri} permanent
}

www.finmates.app {
    redir https://app.finmates.app{uri} permanent
}

app.finmates.app {
    reverse_proxy 127.0.0.1:3000
}

api.finmates.app {
    reverse_proxy 127.0.0.1:8000
}
```

Caddy automatically issues and renews HTTPS certificates.

## Clone

```bash
cd /opt
sudo git clone https://github.com/botirbektulqinov/FinMateUz.git finmateuz
sudo chown -R "$USER":"$USER" /opt/finmateuz
cd /opt/finmateuz
```

## Environment

```bash
cp .env.production.example .env
nano .env
```

Fill these manually with real production values:

- `POSTGRES_PASSWORD`
- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `TELEGRAM_BOT_TOKEN`
- `BOT_API_TOKEN`

Production Docker values must use service hosts:

- `POSTGRES_HOST=postgres`
- `DATABASE_URL=postgresql+psycopg://finmate:<password>@postgres:5432/finmate`
- `REDIS_URL=redis://redis:6379/0`
- `NEXT_PUBLIC_API_URL=https://api.finmates.app/api/v1`
- `API_BASE_URL=https://api.finmates.app/api/v1`
- `CORS_ORIGINS=["https://app.finmates.app","https://finmates.app","https://www.finmates.app"]`

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
- root and `www` return redirects to `https://app.finmates.app`.

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

For real production usage, also enable DigitalOcean volume/server snapshots or move PostgreSQL to a managed database with automated backups and restore testing.

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
- Caddy loaded an old config or DNS does not point to `134.122.92.113`.
