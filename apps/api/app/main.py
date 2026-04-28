import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.api.routes import audit, auth, bot, categories, companies, reports, transactions


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(level=logging.INFO if settings.environment == "local" else logging.WARNING)
    logger = logging.getLogger("finmate.api")
    app = FastAPI(title=settings.app_name, version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled API error")
        if settings.environment == "local":
            raise exc
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    @app.middleware("http")
    async def request_logging(request: Request, call_next):
        started = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        logger.info("%s %s -> %s in %sms", request.method, request.url.path, response.status_code, elapsed_ms)
        return response

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    api_prefix = "/api/v1"
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(companies.router, prefix=api_prefix)
    app.include_router(categories.router, prefix=api_prefix)
    app.include_router(transactions.router, prefix=api_prefix)
    app.include_router(reports.router, prefix=api_prefix)
    app.include_router(audit.router, prefix=api_prefix)
    app.include_router(bot.router, prefix=api_prefix)
    return app


app = create_app()
