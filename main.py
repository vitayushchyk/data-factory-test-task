from fastapi import FastAPI


from routers.health_check_router import health_check_router
from routers.plan_insert_router import load_data_rout

from routers.user_credits_rout import user_credits


def create_app() -> FastAPI:
    app = FastAPI(
        title="Phrase generator API",
        docs_url="/docs",
        description="Phrase generator",
        debug=True,
    )
    app.include_router(health_check_router)
    app.include_router(load_data_rout)

    app.include_router(user_credits)

    return app


app = create_app()
