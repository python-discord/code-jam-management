from fastapi import FastAPI

import api.database as db
from api.routers import codejams, infractions, users


app = FastAPI(docs_url="/docs", redoc_url="/")

app.include_router(codejams.router)
app.include_router(users.router)
app.include_router(infractions.router)


@app.on_event("startup")
async def on_startup() -> None:
    """Initialize the database on startup."""
    async with db.engine.begin() as conn:
        await conn.run_sync(db.Base.metadata.create_all)
