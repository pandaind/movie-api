import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import status
from httpx import ASGITransport, AsyncClient

from app.api.profiler import ProfileEndpointsMiddleWare
from app.main import app
from app.models import profile
from app.models.movie import Movie
from tests.conftests import side_effect_profile_endpoint_middleware


class TestMoviesAPI(unittest.IsolatedAsyncioTestCase):
    payload = {
        "id": 1,
        "title": "Test Movie",
        "genre": "Horror",
        "director": "Test Director",
        "release_year": 2021,
    }

    payloads = [
        {
            "id": 1,
            "title": "Test Movie 1",
            "genre": "Horror",
            "director": "Test Director",
            "release_year": 2021,
        },
        {
            "id": 2,
            "title": "Test Movie 2",
            "genre": "Horror",
            "director": "Test Director",
            "release_year": 2021,
        },
    ]

    @classmethod
    def setUpClass(cls):
        cls.client = AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost:8000"
        )

    @classmethod
    def tearDownClass(cls):
        asyncio.run(cls.client.aclose())

    @patch.object(
        ProfileEndpointsMiddleWare,
        "dispatch",
        side_effect=side_effect_profile_endpoint_middleware,
    )
    @patch(
        "app.api.v1.movies.MovieService.create_movie",
        new_callable=AsyncMock,
        return_value=Movie(**payload),
    )
    @patch(
        "app.security.security.decode_access_token",
        new_callable=AsyncMock,
        return_value={"user_id": 1, profile: None},
    )
    async def test_create_movie(
        self, mock_create_movie, decode_access_token, mock_dispatch
    ):
        response = await self.client.post(
            "/v1/movies/",
            json=self.payload,
            headers={"Authorization": f"Bearer valid_token"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["title"], "Test Movie")

    @patch.object(
        ProfileEndpointsMiddleWare,
        "dispatch",
        side_effect=side_effect_profile_endpoint_middleware,
    )
    @patch(
        "app.api.v1.movies.MovieService.get_all_movies",
        new_callable=AsyncMock,
        return_value=[Movie(**payload) for payload in payloads],
    )
    @patch(
        "app.security.security.decode_access_token",
        new_callable=AsyncMock,
        return_value={"user_id": 1},
    )
    async def test_get_movies(
        self, mock_get_all_movies, decode_access_token, mock_dispatch
    ):
        response = await self.client.get(
            "/v1/movies/", headers={"Authorization": f"Bearer valid_token"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), list)

    @patch.object(
        ProfileEndpointsMiddleWare,
        "dispatch",
        side_effect=side_effect_profile_endpoint_middleware,
    )
    @patch(
        "app.api.v1.movies.MovieService.get_movie_by_id",
        new_callable=AsyncMock,
        return_value=Movie(**payload),
    )
    @patch(
        "app.security.security.decode_access_token",
        new_callable=AsyncMock,
        return_value={"user_id": 1},
    )
    async def test_get_movie(
        self, mock_get_movie_by_id, decode_access_token, mock_dispatch
    ):
        response = await self.client.get(
            "/v1/movies/1", headers={"Authorization": f"Bearer valid_token"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], 1)

    @patch.object(
        ProfileEndpointsMiddleWare,
        "dispatch",
        side_effect=side_effect_profile_endpoint_middleware,
    )
    @patch(
        "app.api.v1.movies.MovieService.get_movies_by_genre",
        new_callable=AsyncMock,
        return_value=[Movie(**payload) for payload in payloads],
    )
    @patch(
        "app.security.security.decode_access_token",
        new_callable=AsyncMock,
        return_value={"user_id": 1},
    )
    async def test_get_movies_by_genre(
        self, mock_get_movies_by_genre, decode_access_token, mock_dispatch
    ):
        response = await self.client.get(
            "/v1/movies/genre/Action", headers={"Authorization": f"Bearer valid_token"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), list)

    @patch.object(
        ProfileEndpointsMiddleWare,
        "dispatch",
        side_effect=side_effect_profile_endpoint_middleware,
    )
    @patch(
        "app.api.v1.movies.MovieService.update_movie",
        new_callable=AsyncMock,
        return_value=Movie(
            **{
                "id": 1,
                "title": "Updated Movie",
                "genre": "Action",
                "director": "Updated Director",
                "release_year": 2021,
            }
        ),
    )
    @patch(
        "app.security.security.decode_access_token",
        new_callable=AsyncMock,
        return_value={"user_id": 1},
    )
    async def test_update_movie(
        self, mock_update_movie, decode_access_token, mock_dispatch
    ):
        response = await self.client.put(
            "/v1/movies/1",
            json={
                "id": 1,
                "title": "Updated Movie",
                "genre": "Action",
                "director": "Updated Director",
                "release_year": 2021,
            },
            headers={"Authorization": f"Bearer valid_token"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["title"], "Updated Movie")

    @patch.object(
        ProfileEndpointsMiddleWare,
        "dispatch",
        side_effect=side_effect_profile_endpoint_middleware,
    )
    @patch(
        "app.api.v1.movies.MovieService.delete_movie",
        new_callable=AsyncMock,
        return_value=Movie(**payload),
    )
    @patch(
        "app.security.security.decode_access_token",
        new_callable=AsyncMock,
        return_value={"user_id": 1},
    )
    async def test_delete_movie(
        self, mock_delete_movie, decode_access_token, mock_dispatch
    ):
        response = await self.client.delete(
            "/v1/movies/1", headers={"Authorization": f"Bearer valid_token"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["message"], "Movie deleted successfully")


if __name__ == "__main__":
    unittest.main()
