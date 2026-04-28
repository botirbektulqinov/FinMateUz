.PHONY: up down prod-up prod-down prod-logs prod-ps prod-restart prod-deploy logs api-test bot-test web-test web-build migrate checks

up:
	docker compose up --build postgres redis api web

down:
	docker compose down

prod-up:
	docker compose -f docker-compose.prod.yml up --build -d

prod-down:
	docker compose -f docker-compose.prod.yml down

prod-logs:
	docker compose -f docker-compose.prod.yml logs -f

prod-ps:
	docker compose -f docker-compose.prod.yml ps

prod-restart:
	docker compose -f docker-compose.prod.yml restart

prod-deploy:
	bash scripts/deploy-production.sh

logs:
	docker compose logs -f api web

migrate:
	docker compose exec api alembic upgrade head

api-test:
	cd apps/api && python -m pytest

bot-test:
	cd apps/bot && python -m pytest

web-test:
	cd apps/web && npm run lint && npm run typecheck && npm run test

web-build:
	cd apps/web && npm run build

checks: api-test bot-test web-test web-build
