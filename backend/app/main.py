"""Точка входа FastAPI: ядро управления «Астрокосмос»."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import get_session_factory, init_database
from app.mqtt.bridge import MqttBridge
from app.services import hall_service
from app.services.hall_loop import run_hall_loop
from app.services.schedule_ticker import run_schedule_ticker
from app.services.seed import seed_example_materials_if_empty, seed_if_empty

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Поднять БД, справочники и MQTT на старте процесса."""

    await init_database()
    factory = get_session_factory()
    async with factory() as session:
        await seed_if_empty(session)
        await seed_example_materials_if_empty(session)

    bridge = MqttBridge()
    bridge.connect()
    app.state.mqtt = bridge

    # Первый пульс до приёма запросов, чтобы карточки сразу были «на связи».
    if settings.hall_emulator_enabled:
        async with factory() as session:
            await hall_service.pulse_stand(session, bridge)

    stop_background = asyncio.Event()
    background_tasks: list[asyncio.Task] = []
    if settings.schedule_ticker_enabled:
        background_tasks.append(
            asyncio.create_task(
                run_schedule_ticker(app, stop_background),
                name="schedule-ticker",
            )
        )
    background_tasks.append(
        asyncio.create_task(run_hall_loop(app, stop_background), name="hall-loop")
    )

    yield

    stop_background.set()
    for task in background_tasks:
        await task


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Единое ядро интерактивного образовательного комплекса «Астрокосмос».",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root() -> dict[str, str]:
    """Краткое описание сервиса для проверки, что процесс жив."""

    return {"name": settings.app_name, "docs": "/docs"}
