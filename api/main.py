import subprocess

from fastapi import FastAPI

from api.routers import codejams, infractions, users


app = FastAPI(docs_url="/docs", redoc_url="/")

app.include_router(codejams.router)
app.include_router(users.router)
app.include_router(infractions.router)


@app.on_event("startup")
async def on_startup() -> None:
    """Initialize the database on startup."""
    subprocess.run(["poetry", "run", "alembic", "upgrade", "head"])
