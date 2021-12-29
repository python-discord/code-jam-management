"""Tests for the users router."""
import pytest
from httpx import AsyncClient
from fastapi import FastAPI

from api import models

pytestmark = pytest.mark.asyncio


async def test_list_users_without_db_entries(client: AsyncClient, app: FastAPI) -> None:
    """No users should be returned when the database is empty."""
    response = await client.get(app.url_path_for("get_users"))

    assert response.status_code == 200
    users = response.json()
    assert not users


async def test_get_nonexistent_user(client: AsyncClient, app: FastAPI) -> None:
    """Getting a nonexistent user should return a 404."""
    response = await client.get(app.url_path_for("get_user", user_id=129841))
    assert response.status_code == 404


async def test_list_users_with_existing_jam(client: AsyncClient, created_codejam: models.CodeJamResponse, app: FastAPI) -> None:
    """Listing users with an existing jam should display the users in the jam."""
    response = await client.get(app.url_path_for("get_users"))
    assert response.status_code == 200
    raw = response.json()
    users = [models.UserResponse(**user) for user in raw]
    assert users


async def test_get_users_from_existing_jam(
        client: AsyncClient, codejam: models.CodeJam, created_codejam: models.CodeJamResponse, app: FastAPI
) -> None:
    """Getting users from an existing jam should return the users properly."""
    for team in codejam.teams:
        for user in team.users:
            response = await client.get(app.url_path_for("get_user", user_id=user.user_id))
            assert response.status_code == 200
            raw = response.json()
            parsed = models.UserResponse(**raw)
            assert parsed.id == user.user_id
