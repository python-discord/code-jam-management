from fastapi import FastAPI

from api.routers import codejams, infractions, users


app = FastAPI(docs_url="/docs", redoc_url="/")

app.include_router(codejams.router)
app.include_router(users.router)
app.include_router(infractions.router)
