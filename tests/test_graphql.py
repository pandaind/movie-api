import pytest

from tests.conftests import integration_test_client, setup_db, test_db_session


@pytest.mark.asyncio
@pytest.mark.integration
async def test_movies_query(integration_test_client, test_db_session, setup_db):
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
    response = await integration_test_client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "movies" in data["data"]
