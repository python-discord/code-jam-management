from typing import Callable

from fastapi import FastAPI, Request, Response

from api.constants import DATABASE_POOL
from api.routers import codejams, infractions, users


app = FastAPI(docs_url="/docs", redoc_url="/")

app.include_router(codejams.router)
app.include_router(users.router)
app.include_router(infractions.router)


@app.on_event("startup")
async def on_startup() -> None:
    """Initialize the DATABASE_POOL on startup."""
    await DATABASE_POOL


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Close the DATABASE_POOL on shutdown."""
    await DATABASE_POOL.close()


@app.middleware("http")
async def setup_data(request: Request, callnext: Callable) -> Response:
    """Get a connection from the pool for every request."""
    try:
        async with DATABASE_POOL.acquire() as connection:
            request.state.db_conn = connection
            return await callnext(request)

    finally:
        request.state.db_conn = None
