import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, Depends

from app.main import app
from app.db.database import get_db, Base
from app.models.movie import Movie
from app.security.security import get_current_user

# Override the get_current_user dependency for testing
async def override_get_current_user():
    return {"username": "testuser", "roles": ["user"]}

app.dependency_overrides[get_current_user] = override_get_current_user

import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

# Use a single engine for the entire test session
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest_asyncio.fixture(scope="session")
async def engine():
    _engine = create_async_engine(DATABASE_URL, echo=False)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    # Clean up the database file after the session
    await _engine.dispose()
    # os.remove("test.db") # Potentially, if we want to ensure file is gone. Requires import os.

@pytest_asyncio.fixture(scope="function")
async def db_session(engine):
    connection = await engine.connect()
    transaction = await connection.begin_nested() # Use nested transaction

    TestingSessionLocal = sessionmaker(
        bind=connection, class_=AsyncSession, expire_on_commit=False
    )
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback() # Rollback the nested transaction
        await connection.close()

# Override the get_db dependency for the FastAPI app
async def override_get_db_for_app(db: AsyncSession = Depends(db_session)):
    yield db

app.dependency_overrides[get_db] = override_get_db_for_app


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# Tests for create_movie endpoint
@pytest.mark.asyncio
async def test_create_movie_success(client: AsyncClient, db_session: AsyncSession):
    movie_data = {
        "title": "Test Movie",
        "genre": "Test Genre",
        "director": "Test Director",
        "release_year": 2023,
    }
    response = await client.post("/api/v1/movies/", json=movie_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == movie_data["title"]
    assert data["genre"] == movie_data["genre"]
    assert data["director"] == movie_data["director"]
    assert data["release_year"] == movie_data["release_year"]
    assert "id" in data

    movie_in_db = await db_session.get(Movie, data["id"])
    assert movie_in_db is not None
    assert movie_in_db.title == movie_data["title"]

@pytest.mark.asyncio
async def test_create_movie_already_exists(client: AsyncClient, db_session: AsyncSession):
    movie_data = {
        "title": "Existing Movie",
        "genre": "Test Genre",
        "director": "Test Director",
        "release_year": 2023,
    }
    # Create the movie first in the current transaction
    new_movie = Movie(**movie_data)
    db_session.add(new_movie)
    await db_session.commit()
    await db_session.refresh(new_movie)

    # Attempt to create the same movie again via API
    response = await client.post("/api/v1/movies/", json=movie_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Movie with title 'Existing Movie' already exists" in response.json()["detail"]


# Tests for get_movies endpoint
@pytest.mark.asyncio
async def test_get_movies_empty(client: AsyncClient):
    response = await client.get("/api/v1/movies/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

@pytest.mark.asyncio
async def test_get_movies_with_data(client: AsyncClient, db_session: AsyncSession):
    movie1_data = {"title": "Movie 1", "genre": "Genre 1", "director": "Director 1", "release_year": 2020}
    movie2_data = {"title": "Movie 2", "genre": "Genre 2", "director": "Director 2", "release_year": 2021}

    db_session.add_all([Movie(**movie1_data), Movie(**movie2_data)])
    await db_session.commit()

    response = await client.get("/api/v1/movies/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    # Order isn't guaranteed, so check titles present
    titles = {item['title'] for item in data}
    assert movie1_data["title"] in titles
    assert movie2_data["title"] in titles


# Tests for get_movie endpoint
@pytest.mark.asyncio
async def test_get_movie_success(client: AsyncClient, db_session: AsyncSession):
    movie_data = {
        "title": "Specific Movie",
        "genre": "Test Genre",
        "director": "Test Director",
        "release_year": 2023,
    }
    new_movie = Movie(**movie_data)
    db_session.add(new_movie)
    await db_session.commit()
    await db_session.refresh(new_movie)
    movie_id = new_movie.id

    response = await client.get(f"/api/v1/movies/{movie_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == movie_id
    assert data["title"] == movie_data["title"]

@pytest.mark.asyncio
async def test_get_movie_not_found(client: AsyncClient):
    non_existent_id = 99999
    response = await client.get(f"/api/v1/movies/{non_existent_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Movie with id {non_existent_id} not found"


# Tests for get_movies_by_genre endpoint
@pytest.mark.asyncio
async def test_get_movies_by_genre_success(client: AsyncClient, db_session: AsyncSession):
    movie1_data = {"title": "Action Movie 1", "genre": "Action", "director": "Director A", "release_year": 2022}
    movie2_data = {"title": "Comedy Movie 1", "genre": "Comedy", "director": "Director B", "release_year": 2023}
    movie3_data = {"title": "Action Movie 2", "genre": "Action", "director": "Director C", "release_year": 2023}

    db_session.add_all([Movie(**movie1_data), Movie(**movie2_data), Movie(**movie3_data)])
    await db_session.commit()

    response = await client.get("/api/v1/movies/genre/Action")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    titles = {item['title'] for item in data}
    assert "Action Movie 1" in titles
    assert "Action Movie 2" in titles

@pytest.mark.asyncio
async def test_get_movies_by_genre_not_found(client: AsyncClient):
    non_existent_genre = "NonExistentGenre"
    response = await client.get(f"/api/v1/movies/genre/{non_existent_genre}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"No movies found with genre '{non_existent_genre}'"


# Tests for update_movie endpoint
@pytest.mark.asyncio
async def test_update_movie_success(client: AsyncClient, db_session: AsyncSession):
    original_movie_data = {
        "title": "Original Title",
        "genre": "Original Genre",
        "director": "Original Director",
        "release_year": 2000,
    }
    new_movie = Movie(**original_movie_data)
    db_session.add(new_movie)
    await db_session.commit()
    await db_session.refresh(new_movie)
    movie_id = new_movie.id

    updated_movie_payload = { # Payload sent to API
        "id": movie_id,
        "title": "Updated Title",
        "genre": "Updated Genre",
        "director": "Updated Director",
        "release_year": 2024,
    }
    response = await client.put(f"/api/v1/movies/{movie_id}", json=updated_movie_payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == updated_movie_payload["title"]
    assert data["genre"] == updated_movie_payload["genre"]
    assert data["director"] == updated_movie_payload["director"]
    assert data["release_year"] == updated_movie_payload["release_year"]

    movie_in_db = await db_session.get(Movie, movie_id)
    assert movie_in_db is not None
    assert movie_in_db.title == updated_movie_payload["title"]

@pytest.mark.asyncio
async def test_update_movie_not_found(client: AsyncClient):
    non_existent_id = 88888
    updated_movie_data = {
        "id": non_existent_id,
        "title": "Non Existent",
        "genre": "Non Existent",
        "director": "Non Existent",
        "release_year": 2000,
    }
    response = await client.put(f"/api/v1/movies/{non_existent_id}", json=updated_movie_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Movie with id {non_existent_id} not found"

@pytest.mark.asyncio
async def test_update_movie_invalid_data(client: AsyncClient, db_session: AsyncSession):
    movie_data = {
        "title": "Movie To Update With Invalid Data",
        "genre": "Test Genre",
        "director": "Test Director",
        "release_year": 2023,
    }
    new_movie = Movie(**movie_data)
    db_session.add(new_movie)
    await db_session.commit()
    await db_session.refresh(new_movie)
    movie_id = new_movie.id

    invalid_update_data = {
        "id": movie_id,
        "genre": "Updated Genre Only", # title is missing
    }
    response = await client.put(f"/api/v1/movies/{movie_id}", json=invalid_update_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# Tests for delete_movie endpoint
@pytest.mark.asyncio
async def test_delete_movie_success(client: AsyncClient, db_session: AsyncSession):
    movie_data = {
        "title": "Movie to Delete",
        "genre": "Test Genre",
        "director": "Test Director",
        "release_year": 2023,
    }
    new_movie = Movie(**movie_data)
    db_session.add(new_movie)
    await db_session.commit()
    await db_session.refresh(new_movie)
    movie_id = new_movie.id

    response = await client.delete(f"/api/v1/movies/{movie_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Movie deleted successfully"}

    movie_in_db = await db_session.get(Movie, movie_id)
    assert movie_in_db is None

@pytest.mark.asyncio
async def test_delete_movie_not_found(client: AsyncClient):
    non_existent_id = 77777
    response = await client.delete(f"/api/v1/movies/{non_existent_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Movie with id {non_existent_id} not found"


# Tests for get_info_i18n endpoint
@pytest.mark.asyncio
@pytest.mark.parametrize("language, expected_create_text", [
    ("en-US,en;q=0.9", "Create a new movie"),
    ("fr-FR,fr;q=0.9", "Créer un nouveau film"),
    ("en", "Create a new movie"),
    ("fr", "Créer un nouveau film"),
])
async def test_get_info_i18n(client: AsyncClient, language: str, expected_create_text: str):
    headers = {"Accept-Language": language}
    response = await client.get("/api/v1/movies/i18n/info", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["movies"]["create"] == expected_create_text

@pytest.mark.asyncio
async def test_get_info_i18n_default_language(client: AsyncClient):
    response = await client.get("/api/v1/movies/i18n/info")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["movies"]["create"] == "Create a new movie"

@pytest.mark.asyncio
async def test_get_info_i18n_unsupported_language(client: AsyncClient):
    headers = {"Accept-Language": "es-ES,es;q=0.9"}
    response = await client.get("/api/v1/movies/i18n/info", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["movies"]["create"] == "Create a new movie"


# Tests for show_currency endpoint
@pytest.mark.asyncio
@pytest.mark.parametrize("language, expected_currency, expected_currency_name", [
    ("en-US,en;q=0.9", "USD", "US Dollar"),
    ("fr-FR,fr;q=0.9", "EUR", "Euro"),
    ("en", "USD", "US Dollar"),
    ("fr", "EUR", "Euro"),
])
async def test_show_currency(client: AsyncClient, language: str, expected_currency: str, expected_currency_name: str):
    headers = {"Accept-Language": language}
    response = await client.get("/api/v1/movies/i18n/currency", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["currency"] == expected_currency
    assert data["currency_name"] == expected_currency_name

@pytest.mark.asyncio
async def test_show_currency_default_language(client: AsyncClient):
    response = await client.get("/api/v1/movies/i18n/currency")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["currency"] == "USD"
    assert data["currency_name"] == "US Dollar"

@pytest.mark.asyncio
async def test_show_currency_unsupported_language(client: AsyncClient):
    headers = {"Accept-Language": "es-ES,es;q=0.9"}
    response = await client.get("/api/v1/movies/i18n/currency", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["currency"] == "USD"
    assert data["currency_name"] == "US Dollar"
