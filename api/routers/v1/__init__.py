from fastapi import APIRouter

from api.routers.v1 import codejams, infractions, teams, users, winners

v1_routes_router = APIRouter()
v1_routes_router.include_router(codejams.router)
v1_routes_router.include_router(infractions.router)
v1_routes_router.include_router(teams.router)
v1_routes_router.include_router(users.router)
v1_routes_router.include_router(winners.router)
