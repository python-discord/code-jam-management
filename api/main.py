from fastapi import FastAPI
from starlette.middleware.authentication import AuthenticationMiddleware

from api.constants import TOKEN
from api.middleware import TokenAuthentication, on_auth_error
from api.routers import codejams, infractions, teams, users, winners

app = FastAPI(redoc_url="/", docs_url="/swagger")

app.add_middleware(
    AuthenticationMiddleware,
    backend=TokenAuthentication(token=TOKEN),
    on_error=on_auth_error,
)

app.include_router(codejams.router)
app.include_router(infractions.router)
app.include_router(teams.router)
app.include_router(users.router)
app.include_router(winners.router)
