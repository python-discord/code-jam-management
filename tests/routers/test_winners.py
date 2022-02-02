"""Tests for the users router."""
import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from api import models

pytestmark = pytest.mark.asyncio


async def test_get_winners_with_nonexistant_jam(client: AsyncClient, app: FastAPI) -> None:
    """Getting winners from a nonexistant codejam should return a 404."""
    response = await client.get(app.url_path_for("get_winners", jam_id=123421))
    assert response.status_code == 404


async def test_get_winners_with_existing_jam(
    client: AsyncClient, app: FastAPI, created_codejam: models.CodeJamResponse
) -> None:
    """Getting winners from a codejam that was just created should return an empty list."""
    response = await client.get(app.url_path_for("get_winners", jam_id=created_codejam.id))
    assert response.status_code == 200
    assert not response.json()


async def test_get_winners_with_existing_winner(
    client: AsyncClient, app: FastAPI, created_winner: models.WinnerResponse
) -> None:
    """Getting winners from a codejam that has a winner should return that winner."""
    response = await client.get(app.url_path_for("get_winners", jam_id=created_winner.jam_id))
    assert response.status_code == 200

    raw = response.json()[0]
    assert models.WinnerResponse(**raw) == created_winner


async def test_create_winners_with_nonexistant_jam(client: AsyncClient, app: FastAPI) -> None:
    """Adding winners to a nonexistant codejam should return a 404."""
    response = await client.post(app.url_path_for("create_winners", jam_id=1247241), json=[])
    assert response.status_code == 404


async def test_create_winners_with_empty_list(
    client: AsyncClient, app: FastAPI, created_codejam: models.CodeJamResponse
) -> None:
    """Adding an empty list to winners should return a 400."""
    response = await client.post(app.url_path_for("create_winners", jam_id=created_codejam.id), json=[])
    assert response.status_code == 400


async def test_create_winners_with_duplicates(
    client: AsyncClient, app: FastAPI, created_codejam: models.CodeJamResponse
) -> None:
    """Adding duplicate winners should return a 400."""
    winner = {
        "user_id": created_codejam.teams[0].users[0].user_id,
        "first_place": False
    }

    response = await client.post(
        app.url_path_for("create_winners", jam_id=created_codejam.id), json=[winner, winner]
    )

    assert response.status_code == 400


async def test_create_winners_with_existing_winner(
    client: AsyncClient, app: FastAPI, created_winner: models.WinnerResponse
) -> None:
    """Adding a winner that already exists in the jam should return a 409."""
    response = await client.post(
        app.url_path_for("create_winners", jam_id=created_winner.jam_id), json=[
            created_winner.dict(exclude={"jam_id"})
        ]
    )
    assert response.status_code == 409
