"""Tests for the users router."""
import pytest
from httpx import AsyncClient

from api import models


@pytest.mark.asyncio
async def test_list_users_without_db_entries(client: AsyncClient) -> None:
    """No users should be returned when the database is empty."""
    response = await client.get('/users')

    assert response.status_code == 200
    users = response.json()
    assert not users


@pytest.mark.asyncio
async def test_get_nonexistent_user(client: AsyncClient) -> None:
    """Getting a nonexistent user should return a 404."""
    response = await client.get('/users/129841')
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_users_with_existing_jam(client: AsyncClient, created_codejam: models.CodeJamResponse) -> None:
    """Listing users with an existing jam should display the users in the jam."""
    response = await client.get('/users')
    assert response.status_code == 200
    raw = response.json()
    users = [models.UserResponse(**user) for user in raw]
    assert users


@pytest.mark.asyncio
async def test_get_users_from_existing_jam(
    client: AsyncClient, codejam: models.CodeJam, created_codejam: models.CodeJamResponse
) -> None:
    """Getting users from an existing jam should return the users properly."""
    for team in codejam.teams:
        for user in team.users:
            response = await client.get(f'/users/{user.user_id}')
            assert response.status_code == 200
            raw = response.json()
            parsed = models.UserResponse(**raw)
            assert parsed.user_id == user.user_id
