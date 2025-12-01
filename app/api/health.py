"""Health check endpoint для мониторинга состояния сервиса."""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """
    Проверка состояния сервиса.

    Возвращает:
        dict: Статус сервиса
    """
    return {"status": "ok"}
