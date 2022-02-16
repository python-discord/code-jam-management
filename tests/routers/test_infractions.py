"""Tests for the infractions router."""
import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from api import models

pytestmark = pytest.mark.asyncio


async def test_list_infractions_without_db_entries(client: AsyncClient, app: FastAPI) -> None:
    """No infractions should be returned when the database is empty."""
    response = await client.get(app.url_path_for("get_infractions"))
    infractions = response.json()
    assert response.status_code == 200
    assert not infractions


async def test_get_nonexsistent_infraction(client: AsyncClient, app: FastAPI) -> None:
    """Getting a nonexistent infraction should return a 404."""
    response = await client.get(app.url_path_for("get_infraction", infraction_id=41902))
    assert response.status_code == 404


async def test_get_existent_infraction(
    client: AsyncClient,
    app: FastAPI,
    created_infraction: models.InfractionResponse
) -> None:
    """Getting an existing infraction should return 200."""
    response = await client.get(app.url_path_for("get_infraction", infraction_id=created_infraction.id))
    assert response.status_code == 200


async def test_create_infractions_rejects_invalid_data(client: AsyncClient, app: FastAPI) -> None:
    """Posting invalid JSON data should return 422."""
    response = await client.post(app.url_path_for("create_infraction"), json={"reason": "Yes"})
    assert response.status_code == 422
