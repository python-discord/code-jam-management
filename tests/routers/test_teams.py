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


async def test_list_team_users_without_db_entries(client: AsyncClient, app: FastAPI) -> None:
    """No team users should be returned when the database is empty."""
    response = await client.get(app.url_path_for("get_team_users", team_id=54321))
    assert response.status_code == 404


async def test_add_user_to_nonexistent_team(client: AsyncClient, app: FastAPI) -> None:
    """Adding a user to a nonexistent team should return a 404."""
    response = await client.post(app.url_path_for("add_user_to_team", team_id=123826, user_id=123124))
    assert response.status_code == 404


async def test_remove_user_from_nonexistent_team(client: AsyncClient, app: FastAPI) -> None:
    """Deleting a user from a nonexistent team should return a 404."""
    response = await client.delete(app.url_path_for("remove_user_from_team", team_id=123826, user_id=123124))
    assert response.status_code == 404


async def test_get_team_with_existing_jam(
    client: AsyncClient, app: FastAPI, created_codejam: models.CodeJamResponse
) -> None:
    """Getting an existing infraction should return 200."""
    team = created_codejam.teams[0]
    response = await client.get(app.url_path_for("get_team", team_id=team.id))
    assert response.status_code == 200

    parsed = models.TeamResponse(**response.json())
    assert parsed == team


async def test_list_team_with_existing_jam(
    client: AsyncClient, app: FastAPI, created_codejam: models.CodeJamResponse
) -> None:
    """Getting an existing team should return 200."""
    response = await client.get(app.url_path_for("get_teams"))
    assert response.status_code == 200

    raw = response.json()
    assert created_codejam.teams == [models.TeamResponse(**team) for team in raw]


async def test_add_user_to_team(
    client: AsyncClient,
    app: FastAPI,
    created_codejam: models.CodeJamResponse,
) -> None:
    """Adding a user to a team should return 200."""
    team_1, team_2 = created_codejam.teams
    user = team_1.users[0]

    response = await client.post(
        app.url_path_for("add_user_to_team", team_id=team_2.id, user_id=user.user_id),
        params={"is_leader": user.is_leader},
    )

    assert response.status_code == 200

    raw = response.json()
    parsed = models.User(**raw)
    assert parsed == user


async def test_remove_user_from_team(
    client: AsyncClient,
    app: FastAPI,
    created_codejam: models.CodeJamResponse,
) -> None:
    """Removing a user from a team should return 204."""
    team = created_codejam.teams[0]
    user = team.users[0]

    response = await client.delete(app.url_path_for("remove_user_from_team", team_id=team.id, user_id=user.user_id))

    assert response.status_code == 204

    response = await client.get(app.url_path_for("get_team_users", team_id=team.id))
    assert response.status_code == 200

    raw = response.json()
    parsed = [models.User(**user) for user in raw]

    assert user not in parsed


async def test_add_existing_team_user(
    client: AsyncClient,
    app: FastAPI,
    created_codejam: models.CodeJamResponse,
) -> None:
    """Adding a user to a team that the user is already in should return 400."""
    team = created_codejam.teams[0]
    user = team.users[0]

    response = await client.post(
        app.url_path_for("add_user_to_team", team_id=team.id, user_id=user.user_id),
        params={"is_leader": user.is_leader},
    )

    assert response.status_code == 400


async def test_remove_nonexisting_team_user(
    client: AsyncClient,
    app: FastAPI,
    created_codejam: models.CodeJamResponse,
) -> None:
    """Removing a user from a team that the user is not in should return 400."""
    team = created_codejam.teams[0]
    user = created_codejam.teams[1].users[0]

    response = await client.delete(app.url_path_for("remove_user_from_team", team_id=team.id, user_id=user.user_id))

    assert response.status_code == 400


async def test_find_nonexisting_team(client: AsyncClient, app: FastAPI) -> None:
    """Getting a non-existing team by name should return 404."""
    response = await client.get(app.url_path_for("find_team_by_name"), params={"name": "team that should never exist"})

    assert response.status_code == 404


async def test_find_existing_team_case_insensitive_current_jam(
    client: AsyncClient, app: FastAPI, created_codejam: models.CodeJamResponse
) -> None:
    """Getting an existing team (current jam) should return 200 and be case-insensitive."""
    team = created_codejam.teams[0]

    response = await client.get(app.url_path_for("find_team_by_name"), params={"name": team.name.upper()})
    assert response.status_code == 200

    parsed = models.TeamResponse(**response.json())
    assert parsed == team


async def test_find_team_by_name_wrong_jam(
    client: AsyncClient, app: FastAPI, created_codejam: models.CodeJamResponse
) -> None:
    """Getting an existing team from wrong code jam should return 404."""
    response = await client.get(
        app.url_path_for("find_team_by_name"), params={"name": created_codejam.teams[0].name.upper(), "jam_id": 9999}
    )
    assert response.status_code == 404


async def test_find_team_by_name_using_specific_jam(
    client: AsyncClient, app: FastAPI, created_codejam: models.CodeJamResponse
) -> None:
    """Getting an existing team using right jam ID should return 200 and be case-insensitive."""
    team = created_codejam.teams[0]

    response = await client.get(
        app.url_path_for("find_team_by_name"), params={"name": team.name.upper(), "jam_id": created_codejam.id}
    )
    assert response.status_code == 200

    parsed = models.TeamResponse(**response.json())
    assert parsed == team
