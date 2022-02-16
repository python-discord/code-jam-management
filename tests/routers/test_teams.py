"""Tests for the infractions router."""
import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from api import models

pytestmark = pytest.mark.asyncio


async def test_list_teams_without_db_entries(client: AsyncClient, app: FastAPI) -> None:
    """No teams should be returned when the database is empty."""
    response = await client.get(app.url_path_for("get_infractions"))
    infractions = response.json()
    assert response.status_code == 200
    assert not infractions


async def test_get_nonexsistent_teams(client: AsyncClient, app: FastAPI) -> None:
    """Getting a nonexistent team should return a 404."""
    response = await client.get(app.url_path_for("get_team", team_id=123826))
    assert response.status_code == 404


async def test_get_team_with_existing_jam(
    client: AsyncClient,
    app: FastAPI,
    created_codejam: models.CodeJamResponse
) -> None:
    """Getting an existing infraction should return 200."""
    team = created_codejam.teams[0]
    response = await client.get(app.url_path_for("get_team", team_id=team.id))
    assert response.status_code == 200

    parsed = models.TeamResponse(**response.json())
    assert parsed == team


async def test_list_team_with_existing_jam(
    client: AsyncClient,
    app: FastAPI,
    created_codejam: models.CodeJamResponse
) -> None:
    """Getting an existing team should return 200."""
    response = await client.get(app.url_path_for("get_teams"))
    assert response.status_code == 200

    raw = response.json()
    assert created_codejam.teams == [models.TeamResponse(**team) for team in raw]
