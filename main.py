from fastapi import FastAPI


from config.logging_config import LoggerConfigurator
from routers.health_check_router import health_check_router
from routers.user_credits_rout import user_credits

logger = LoggerConfigurator.setup_logger(__name__, to_file="logs/log")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Phrase generator API",
        docs_url="/docs",
        description="Phrase generator",
        debug=True,
    )
    app.include_router(health_check_router)
    app.include_router(user_credits)

    return app


app = create_app()
