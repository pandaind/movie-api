from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import MovieNotFoundException
from app.core.logger import logger
from app.models.movie import Movie


class MovieService:
    @classmethod
    async def create_movie(cls, movie: Movie, db: AsyncSession):
        db.add(movie)
        await db.commit()  # Commit the transaction
        await db.refresh(movie)  # Refresh to get the ID of the new movie
        logger.info(f"Movie '{movie.title}' created successfully.")
        return movie

    @classmethod
    async def get_all_movies(cls, db: AsyncSession):
        result = await db.execute(select(Movie))
        movies = result.scalars().all()  # Get all movies as a list
        return movies

    @classmethod
    async def get_movie_by_id(cls, movie_id: int, db: AsyncSession):
        logger.debug(f"Fetching movie with ID {movie_id}")
        result = await db.execute(select(Movie).where(Movie.id == movie_id))
        movie = result.scalar_one_or_none()
        if movie is None:
            logger.error(f"Movie with ID {movie_id} not found.")
            raise MovieNotFoundException(movie_id)
        return movie

    @classmethod
    async def update_movie(cls, movie_id: int, updated_movie: Movie, db: AsyncSession):
        result = await db.execute(select(Movie).where(Movie.id == movie_id))
        movie = result.scalar_one_or_none()
        if movie is None:
            raise MovieNotFoundException(movie_id)

        movie.title = updated_movie.title
        movie.director = updated_movie.director
        movie.release_year = updated_movie.release_year
        await db.commit()
        await db.refresh(movie)
        return movie

    @classmethod
    async def delete_movie(cls, movie_id: int, db: AsyncSession):
        result = await db.execute(select(Movie).where(Movie.id == movie_id))
        movie = result.scalar_one_or_none()

        if movie is not None:
            await db.delete(movie)
            await db.commit()

        return movie
