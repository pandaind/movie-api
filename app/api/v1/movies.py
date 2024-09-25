from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import MovieNotFoundException, MovieAlreadyExistsException
from app.db.database import get_db
from app.models.movie import Movie, MovieSchema, CreateMovie
from app.services.movies_services import MovieService

router = APIRouter()


@router.post("/", response_model=CreateMovie, summary="Add a new movie (v1)",
             description="Create a new movie entry by providing its details.")
async def create_movie(movie: CreateMovie, db: AsyncSession = Depends(get_db)):
    """
    Create a new movie entry by providing its details.

    Args:
        movie (Movie): The movie object to be created.

    Returns:
        Movie: The created movie object.

    Raises:
        HTTPException: If a movie with the same ID already exists, raises a 400 error.
        :param movie:
        :param db:
    """
    response = await MovieService.create_movie(movie, db)
    if response is None:
        raise MovieAlreadyExistsException(movie.title)
    return response


@router.get("/", response_model=List[MovieSchema], summary="Get all movies (v1)",
            description="Retrieve a list of all movies in the version 1 database.")
async def get_movies(db: AsyncSession = Depends(get_db)):
    """
    Retrieve a list of all movies in the version 1 database.

    Returns:
        List[Movie]: A list of all movie objects in the database.
    """
    return await MovieService.get_all_movies(db)


@router.get("/{movie_id}", response_model=MovieSchema, summary="Get a movie by ID (v1)",
            description="Retrieve details of a specific movie by its ID in version 1.",
            responses={404: {"description": "Movie not found"}})
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve details of a specific movie by its ID in version 1.

    Args:
        movie_id (int): The unique ID of the movie to be retrieved.

    Returns:
        Movie: The movie object if found.

    Raises:
        HTTPException: If the movie with the specified ID is not found, raises a 404 error.
        :param movie_id:
        :param db:
    """
    movie = await MovieService.get_movie_by_id(movie_id, db)
    if movie is None:
        raise MovieNotFoundException(movie_id)
    return movie


@router.put("/{movie_id}", response_model=MovieSchema, summary="Update a movie (v1)",
            description="Update the details of an existing movie by its ID in version 1.",
            responses={404: {"description": "Movie not found"}})
async def update_movie(movie_id: int, updated_movie: MovieSchema, db: AsyncSession = Depends(get_db)):
    """
    Update a movie by its ID in version 1.

    Args:
        movie_id (int): The unique ID of the movie to be updated.
        updated_movie (Movie): The movie object with updated details.

    Returns:
        Movie: The updated movie object if found.

    Raises:
        HTTPException: If the movie with the specified ID is not found, raises a 404 error.
        :param movie_id:
        :param updated_movie:
        :param db:
    """
    movie = await MovieService.update_movie(movie_id, updated_movie, db)
    if movie is None:
        raise MovieNotFoundException(movie_id)


@router.delete("/{movie_id}", response_model=MovieSchema, summary="Delete a movie (v1)",
               description="Delete a movie from the database by its ID in version 1.",
               responses={404: {"description": "Movie not found"}})
async def delete_movie_v1(movie_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a movie from the database by its ID in version 1.

    Args:
        movie_id (int): The unique ID of the movie to be deleted.
        :param movie_id:
        :param db:
    """
    movie = await MovieService.delete_movie(movie_id, db)
    if movie is not None:
        raise MovieNotFoundException(movie_id)
