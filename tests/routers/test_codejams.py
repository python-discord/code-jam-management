"""Tests for the codejams router."""
import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from api import models

pytestmark = pytest.mark.asyncio


# This test fails when the database already has entries in it.
# If the database has entries in it, cleanup was not performed properly!
async def test_list_codejams_without_db_entries(client: AsyncClient, app: FastAPI) -> None:
    """No codejams should be returned when the database is empty."""
    response = await client.get('/codejams')
    jams = response.json()

    assert response.status_code == 200
    assert not jams


async def test_get_nonexistent_code_jam(client: AsyncClient) -> None:
    """Getting a nonexistent code jam should return a 404."""
    response = await client.get('/codejams/41902')
    assert response.status_code == 404


async def test_get_existing_code_jam(client: AsyncClient, created_codejam: models.CodeJamResponse) -> None:
    """Getting an existing code jam should return 200."""
    response = await client.get(f'/codejams/{created_codejam.id}')
    assert response.status_code == 200
    raw = response.json()
    jam = models.CodeJamResponse(**raw)
    assert jam == created_codejam


async def test_list_codejams_with_existing_jam(client: AsyncClient, created_codejam: models.CodeJamResponse) -> None:
    """Listing all code jams should return the created jam."""
    response = await client.get('/codejams')
    assert response.status_code == 200
    raw = response.json()

    # We should only have a single jam here.
    # Pattern match to make sure that is true.
    [jam] = [models.CodeJamResponse(**jam) for jam in raw]

    # Ensure the code jam in the "single jam" endpoint matches the
    # code jam we get returned from the API here.
    assert jam == created_codejam
