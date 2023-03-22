from fastapi import APIRouter

from api.routers.old import codejams, infractions, teams, users, winners

old_routes_router = APIRouter()
old_routes_router.include_router(codejams.router)
old_routes_router.include_router(infractions.router)
old_routes_router.include_router(teams.router)
old_routes_router.include_router(users.router)
old_routes_router.include_router(winners.router)
