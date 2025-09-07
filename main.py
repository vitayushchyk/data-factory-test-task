from fastapi import FastAPI


from routers.health_check_router import health_check_router
from routers.plan_insert_router import load_data_rout
from routers.plan_performance_router import plan_perf_rout
from routers.user_credits_rout import user_credits
from routers.year_performance_router import year_performance_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Data Factory test task API",
        docs_url="/docs",
        description="Data Factory test task",
        debug=True,
    )
    app.include_router(health_check_router)
    app.include_router(load_data_rout)
    app.include_router(user_credits)
    app.include_router(plan_perf_rout)
    app.include_router(year_performance_router)
    return app


app = create_app()
