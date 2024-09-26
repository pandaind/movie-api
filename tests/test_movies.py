import unittest
import asyncio
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport
from fastapi import status
from app.main import app
from app.models.movie import Movie

class TestMoviesAPI(unittest.TestCase):
    payload = {
        "id": 1,
        "title": "Test Movie",
        "genre": "Horror",
        "director": "Test Director",
        "release_year": 2021
    }

    payloads = [
        {
            "id": 1,
            "title": "Test Movie 1",
            "genre": "Horror",
            "director": "Test Director",
            "release_year": 2021
        },
        {
            "id": 2,
            "title": "Test Movie 2",
            "genre": "Horror",
            "director": "Test Director",
            "release_year": 2021
        }
    ]

    @classmethod
    def setUpClass(cls):
        cls.client = AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000")

    @classmethod
    def tearDownClass(cls):
        asyncio.run(cls.client.aclose())

    @patch("app.api.v1.movies.get_db", new_callable=AsyncMock)
    @patch("app.api.v1.movies.MovieService.create_movie", new_callable=AsyncMock)
    def test_create_movie(self, mock_create_movie, mock_get_db):
        async def run_test():
            mock_create_movie.return_value = Movie(**self.payload)
            response = await self.client.post("/v1/movies/", json=self.payload)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["title"], "Test Movie")
        asyncio.run(run_test())

    @patch("app.api.v1.movies.get_db", new_callable=AsyncMock)
    @patch("app.api.v1.movies.MovieService.get_all_movies", new_callable=AsyncMock)
    def test_get_movies(self, mock_get_all_movies, mock_get_db):
        async def run_test():
            mock_get_all_movies.return_value = [Movie(**payload) for payload in self.payloads]
            response = await self.client.get("/v1/movies/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIsInstance(response.json(), list)
        asyncio.run(run_test())

    @patch("app.api.v1.movies.get_db", new_callable=AsyncMock)
    @patch("app.api.v1.movies.MovieService.get_movie_by_id", new_callable=AsyncMock)
    def test_get_movie(self, mock_get_movie_by_id, mock_get_db):
        async def run_test():
            mock_get_movie_by_id.return_value = Movie(**self.payload)
            response = await self.client.get("/v1/movies/1")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["id"], 1)
        asyncio.run(run_test())

    @patch("app.api.v1.movies.get_db", new_callable=AsyncMock)
    @patch("app.api.v1.movies.MovieService.get_movies_by_genre", new_callable=AsyncMock)
    def test_get_movies_by_genre(self, mock_get_movies_by_genre, mock_get_db):
        async def run_test():
            mock_get_movies_by_genre.return_value = [Movie(**payload) for payload in self.payloads]
            response = await self.client.get("/v1/movies/genre/Action")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIsInstance(response.json(), list)
        asyncio.run(run_test())

    @patch("app.api.v1.movies.get_db", new_callable=AsyncMock)
    @patch("app.api.v1.movies.MovieService.update_movie", new_callable=AsyncMock)
    def test_update_movie(self, mock_update_movie, mock_get_db):
        async def run_test():
            mock_update_movie.return_value = Movie(**{"id": 1, "title": "Updated Movie", "genre": "Action", "director": "Updated Director", "release_year": 2021})
            response = await self.client.put("/v1/movies/1", json={"id": 1, "title": "Updated Movie", "genre": "Action", "director": "Updated Director", "release_year": 2021})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["title"], "Updated Movie")
        asyncio.run(run_test())

    @patch("app.api.v1.movies.get_db", new_callable=AsyncMock)
    @patch("app.api.v1.movies.MovieService.delete_movie", new_callable=AsyncMock)
    def test_delete_movie(self, mock_delete_movie, mock_get_db):
        async def run_test():
            mock_delete_movie.return_value = Movie(**self.payload)
            response = await self.client.delete("/v1/movies/1")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["message"], "Movie deleted successfully")
        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()