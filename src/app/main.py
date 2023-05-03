# Packages
from traceback import print_exception
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.middleware import Middleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine

# Modules
from app.utils.helper import ReturnValue
from app.config import STATIC_FILES_DIR
from app.apis.apis import router
from app.database import db_instance
from app.workers.celery import celery_app
from app.workers.tasks import run_test_task


async def root():
    return {"Hello": "World"}


# Health checks
def get_alembic_version():
    db_url = db_instance.get_database_url()
    engine = create_engine(db_url)
    conn = engine.connect()
    context = MigrationContext.configure(conn)
    current_rev = context.get_current_revision()

    return current_rev


def celery_healthcheck():
    """Check if celery workers are alive with ping"""
    celery_response = celery_app.control.ping(timeout=0.5)
    if celery_response:
        return celery_response
    else:
        return "No celery tasks currently active."


async def celery_send_test_task():
    """Celery task test example
    Check worker_1 logs for info messages to see if task was successfully entered and exited."""
    run_test_task.delay()
    return "Check worker_1 logs."


async def healthcheck():
    """Basic healthcheck endpoint.
    Connects to DB for alembic version string and pings Celery worker(s) for 'pong' alive response.
    """
    alembic_revision = get_alembic_version()
    celery_response = celery_healthcheck()

    health_response = {
        "alembic_version": alembic_revision,
        "celery_response": celery_response,
    }

    return health_response


async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        # Add logging here
        print_exception(e)
        rv = ReturnValue(False, status.HTTP_500_INTERNAL_SERVER_ERROR,
                         "Something went wrong", repr(e))
        return JSONResponse(rv.to_dict(), status_code=rv.status_code)


routes = [
    APIRoute("/", endpoint=root, methods=["GET"]),
    APIRoute("/health", endpoint=healthcheck, methods=["GET"]),
    APIRoute("/test-task", endpoint=celery_send_test_task, methods=["GET"]),
]

middleware = Middleware(CORSMiddleware)

app = FastAPI(routes=routes, middleware=[middleware])

app.mount("/static", StaticFiles(directory=STATIC_FILES_DIR), name="static")

app.include_router(router)

app.middleware('http')(catch_exceptions_middleware)
