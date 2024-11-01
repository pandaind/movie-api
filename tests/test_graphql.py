import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from app.gql.gql_utils import graphql_app


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(graphql_app, prefix="/graphql")
    return TestClient(app)


@pytest.mark.asyncio
async def test_movies_query(client):
    query = """
    query {
        movies {
            id
            title
            genre
            director
            releaseYear
        }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "movies" in data["data"]
