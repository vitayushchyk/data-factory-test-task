from fastapi import FastAPI

from routers.health_check_router import health_check_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Phrase generator API",
        docs_url="/docs",
        description="Phrase generator",
        debug=True,
    )
    app.include_router(health_check_router)

    return app


app = create_app()
