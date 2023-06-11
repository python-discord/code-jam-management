from fastapi import FastAPI
from starlette.middleware.authentication import AuthenticationMiddleware

from api.middleware import TokenAuthentication, on_auth_error
from api.routers.v1 import v1_routes_router
from api.settings import Server

app = FastAPI(redoc_url="/", docs_url="/swagger")

app.add_middleware(
    AuthenticationMiddleware,
    backend=TokenAuthentication(token=Server.API_TOKEN.get_secret_value()),
    on_error=on_auth_error,
)

app.include_router(v1_routes_router)
