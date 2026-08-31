"""Прокси-эндпоинты к обсерваторному «Диптиху» (внешняя система).

Ядро не дублирует управление куполом/телескопом: только вызывает
клиент `app.integrations.observatory`.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def observatory_status() -> dict[str, str]:
    """Запросить агрегированный статус обсерватории.

    Returns:
        Заглушка до подключения реального API.
    """

    return {"detail": "not_implemented", "source": "observatory_adapter"}
