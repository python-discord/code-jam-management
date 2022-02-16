from fastapi import FastAPI

from api.routers import codejams, infractions, teams, users, winners


app = FastAPI(redoc_url="/", docs_url=None)

app.include_router(codejams.router)
app.include_router(infractions.router)
app.include_router(teams.router)
app.include_router(users.router)
app.include_router(winners.router)
