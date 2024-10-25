import pytest
from fastapi import status

from tests.conftests import setup_db, test_client, test_db_session


async def get_token(test_client):
    payload = {
        "username": "pandaind",
        "password": "hello",
        "client_id": "aks",
        "client_secret": "aks",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = await test_client.post(
        "/v1/security/token", data=payload, headers=headers
    )
    token = response.json()["access_token"]
    return token


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_movie(test_client, test_db_session, setup_db):
    payload = {
        "id": 1,
        "title": "ioeuyrue",
        "genre": "Horror",
        "director": "Test Director",
        "release_year": 2021,
    }
    response = await test_client.post(
        "/v1/movies/",
        json=payload,
        headers={"Authorization": f"Bearer {await get_token(test_client)}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "ioeuyrue"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_movies(test_client, test_db_session, setup_db):
    # Create a movie
    payload = {
        "id": 1,
        "title": "ioeuyrue",
        "genre": "Horror",
        "director": "Test Director",
        "release_year": 2021,
    }
    await test_client.post(
        "/v1/movies/",
        json=payload,
        headers={"Authorization": f"Bearer {await get_token(test_client)}"},
    )
    # Get all movies
    response = await test_client.get(
        "/v1/movies/",
        headers={"Authorization": f"Bearer {await get_token(test_client)}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_movie(test_client, test_db_session, setup_db):
    # Create a movie
    payload = {
        "id": 1,
        "title": "ioeuyrue",
        "genre": "Horror",
        "director": "Test Director",
        "release_year": 2021,
    }
    await test_client.post(
        "/v1/movies/",
        json=payload,
        headers={"Authorization": f"Bearer {await get_token(test_client)}"},
    )
    # Get a movie
    response = await test_client.get(
        "/v1/movies/1",
        headers={"Authorization": f"Bearer {await get_token(test_client)}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_movies_by_genre(test_client, test_db_session, setup_db):
    # Create a movie
    payload = {
        "id": 1,
        "title": "ioeuyrue",
        "genre": "Horror",
        "director": "Test Director",
        "release_year": 2021,
    }
    await test_client.post(
        "/v1/movies/",
        json=payload,
        headers={"Authorization": f"Bearer {await get_token(test_client)}"},
    )
    # Get movies by genre
    response = await test_client.get(
        "/v1/movies/genre/Horror",
        headers={"Authorization": f"Bearer {await get_token(test_client)}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_movie(test_client, test_db_session, setup_db):
    # Create a movie
    payload = {
        "id": 1,
        "title": "ioeuyrue",
        "genre": "Horror",
        "director": "Test Director",
        "release_year": 2021,
    }
    await test_client.post(
        "/v1/movies/",
        json=payload,
        headers={"Authorization": f"Bearer {await get_token(test_client)}"},
    )
    # Update a movie
    payload = {
        "id": 1,
        "title": "Updated Movie",
        "genre": "Action",
        "director": "Updated Director",
        "release_year": 2021,
    }
    response = await test_client.put(
        "/v1/movies/1",
        json=payload,
        headers={"Authorization": f"Bearer {await get_token(test_client)}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Updated Movie"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_movie(test_client, test_db_session, setup_db):
    # Create a movie
    payload = {
        "id": 1,
        "title": "ioeuyrue",
        "genre": "Horror",
        "director": "Test Director",
        "release_year": 2021,
    }
    await test_client.post(
        "/v1/movies/",
        json=payload,
        headers={"Authorization": f"Bearer {await get_token(test_client)}"},
    )
    # Delete a movie
    response = await test_client.delete(
        "/v1/movies/1",
        headers={"Authorization": f"Bearer {await get_token(test_client)}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Movie deleted successfully"
