"""Tests for the codejams router."""
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api import models
from api.database import User

pytestmark = pytest.mark.asyncio


# This test fails when the database already has entries in it.
# If the database has entries in it, cleanup was not performed properly!
async def test_list_codejams_without_db_entries(client: AsyncClient, app: FastAPI) -> None:
    """No codejams should be returned when the database is empty."""
    response = await client.get(app.url_path_for("get_codejams"))
    jams = response.json()

    assert response.status_code == 200
    assert not jams


async def test_get_nonexistent_code_jam(client: AsyncClient, app: FastAPI) -> None:
    """Getting a nonexistent code jam should return a 404."""
    response = await client.get(app.url_path_for("get_codejam", codejam_id=41902))
    assert response.status_code == 404


async def test_get_existing_code_jam(
        client: AsyncClient,
        created_codejam: models.CodeJamResponse,
        app: FastAPI
) -> None:
    """Getting an existing code jam should return 200."""
    response = await client.get(app.url_path_for("get_codejam", codejam_id=created_codejam.id))
    assert response.status_code == 200
    raw = response.json()
    jam = models.CodeJamResponse(**raw)
    assert jam == created_codejam


async def test_list_codejams_with_existing_jam(
        client: AsyncClient,
        created_codejam: models.CodeJamResponse,
        app: FastAPI
) -> None:
    """Listing all code jams should return the created jam."""
    response = await client.get(app.url_path_for("get_codejams"))
    assert response.status_code == 200
    raw = response.json()

    # We should only have a single jam here.
    # Pattern match to make sure that is true.
    [jam] = [models.CodeJamResponse(**jam) for jam in raw]

    # Ensure the code jam in the "single jam" endpoint matches the
    # code jam we get returned from the API here.
    assert jam == created_codejam


async def test_create_codejams_rejects_invalid_data(client: AsyncClient, app: FastAPI) -> None:
    """Posting invalid JSON data should return 422."""
    response = await client.post(app.url_path_for("create_codejam"), json={"name": "test"})
    assert response.status_code == 422


async def test_create_codejams_accepts_valid_data_and_creates_user(
        client: AsyncClient,
        app: FastAPI, session: AsyncSession
) -> None:
    """Posting a valid JSON data should return 200 and the record should exitst in the DB."""
    response = await client.post(app.url_path_for("create_codejam"), json={
        "name": "CodeJam Test",
        "teams": [{"name": "Dramatic Dragonflies", "users": [{"user_id": 1, "is_leader": True}]}]
    })
    assert response.status_code == 200

    # Checks whether the previously added user was actually inserted into the database.
    assert (await session.execute(select(User).where(User.id == 1))).scalars().unique().one_or_none()
