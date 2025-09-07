from contextlib import asynccontextmanager

from fastapi import FastAPI

from db.connection import async_session_maker
from loader.data_loader import DataLoader
from logs.config.logging_config import logger
from routers.health_check_router import health_check_router
from routers.plan_insert_router import load_data_rout
from routers.plan_performance_router import plan_perf_rout
from routers.user_credits_rout import user_credits
from routers.year_perfmance_router import year_performance_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application: beginning data import...")
    loader = DataLoader(session_maker=async_session_maker)
    await loader.import_all()
    logger.info("Data import completed. Application startup finished.")
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Data Factory test task API",
        docs_url="/docs",
        description="Data Factory test task",
        debug=True,
        lifespan=lifespan,
    )
    app.include_router(health_check_router)
    app.include_router(load_data_rout)
    app.include_router(user_credits)
    app.include_router(plan_perf_rout)
    app.include_router(year_performance_router)
    return app


app = create_app()
