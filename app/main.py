"""Главное приложение FastAPI для интеграции amoCRM → Платформа."""

import logging

from fastapi import FastAPI

from app.api import amo_webhook, health
from app.settings import settings

logging.basicConfig(
    level=settings.log_level_value,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="amoCRM Payment Webhook",
    description="Сервис для обработки webhook от amoCRM и отправки данных на платформу",
    version="1.0.0",
)

app.include_router(health.router)
app.include_router(amo_webhook.router)


@app.on_event("startup")
async def startup_event() -> None:
    """Инициализация при запуске приложения."""
    logger.info("Запуск amoCRM Payment Webhook сервиса")
    logger.info("AMO_BASE_URL: %s", settings.AMO_BASE_URL)
    logger.info("PLATFORM_URL: %s", settings.PLATFORM_URL)
    logger.info("LOG_LEVEL: %s", settings.LOG_LEVEL)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Очистка ресурсов при остановке приложения."""
    logger.info("Остановка amoCRM Payment Webhook сервиса")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
