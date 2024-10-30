from typing import Annotated, List

from babel.numbers import get_currency_name
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.api.internationalization import resolve_accept_language
from app.api.rate_limit import limiter
from app.core.exceptions import MovieNotFoundException
from app.core.logger import background_task
from app.db.database import get_db
from app.models.movie import CreateMovie, Movie, MovieSchema
from app.security.security import get_current_user
from app.services.movies_services import MovieService

router = APIRouter()


@router.post(
    "/",
    response_model=MovieSchema,
    summary="Add a new movie (v1)",
    description="Create a new movie entry by providing its details.",
)
async def create_movie(
    movie_data: CreateMovie,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    """
    Create a new movie entry by providing its details.

    Args:
        movie_data (CreateMovie): The movie object to be created.
        db (AsyncSession): The database session.

    Returns:
        Movie: The created movie object.

    Raises:
        HTTPException: If a movie with the same ID already exists, raises a 400 error.
        :param _user:
        :param movie_data:
        :param db:
    """
    movie = Movie(**movie_data.model_dump())
    response = await MovieService.create_movie(movie, db)
    return response



@router.get(
    "/",
    response_model=List[MovieSchema],
    summary="Get all movies (v1)",
    description="Retrieve a list of all movie s in the version 1 database.",
)
async def get_movies(
    db: AsyncSession = Depends(get_db), _user=Depends(get_current_user)
):
    """
    Retrieve a list of all movies in the version 1 database.

    Returns:
        List[Movie]: A list of all movie objects in the database.
    """
    return await MovieService.get_all_movies(db)


@router.get(
    "/{movie_id}",
    response_model=MovieSchema,
    summary="Get a movie by ID (v1)",
    description="Retrieve details of a specific movie by its ID in version 1.",
    responses={404: {"description": "Movie not found"}},
)
async def get_movie(
    movie_id: int, db: AsyncSession = Depends(get_db), _user=Depends(get_current_user)
):
    """
    Retrieve details of a specific movie by its ID in version 1.

    Args:
        movie_id (int): The unique ID of the movie to be retrieved.

    Returns:
        Movie: The movie object if found.

    Raises:
        HTTPException: If the movie with the specified ID is not found, raises a 404 error.
        :param _user:
        :param movie_id:
        :param db:
    """
    movie = await MovieService.get_movie_by_id(movie_id, db)
    if movie is None:
        raise MovieNotFoundException(movie_id)
    return movie


@router.get(
    "/genre/{genre}",
    response_model=List[MovieSchema],
    summary="Get movies by genre (v1)",
    description="Retrieve a list of movies by genre in version 1.",
    responses={404: {"description": "No movies found"}},
)
async def get_movies_by_genre(
    genre: str, db: AsyncSession = Depends(get_db), _user=Depends(get_current_user)
):
    """
    Retrieve a list of movies by genre in version 1.

    Args:
        genre (str): The genre of movies to be retrieved.

    Returns:
        List[Movie]: A list of movie objects with the specified genre.

    Raises:
        HTTPException: If no movies with the specified genre are found, raises a 404 error.
        :param _user:
        :param genre:
        :param db:
    """
    movies = await MovieService.get_movies_by_genre(genre, db)
    if not movies:
        raise HTTPException(
            status_code=404, detail=f"No movies found with genre '{genre}'"
        )
    return movies


@router.put(
    "/{movie_id}",
    response_model=MovieSchema,
    summary="Update a movie (v1)",
    description="Update the details of an existing movie by its ID in version 1.",
    responses={404: {"description": "Movie not found"}},
)
async def update_movie(
    movie_id: int,
    movie_data: MovieSchema,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    """
    Update a movie by its ID in version 1.

    Args:
        movie_id (int): The unique ID of the movie to be updated.
        movie_data (MovieSchema): The movie object with updated details.
        db (AsyncSession): The database session.

    Returns:
        Movie: The updated movie object if found.

    Raises:
        HTTPException: If the movie with the specified ID is not found, raises a 404 error.
        :param _user:
        :param movie_id:
        :param movie_data:
        :param db:
    """
    if movie_data is None:
        raise HTTPException(
            status_code=400, detail="Invalid input: movie_data is required"
        )

    updated_movie = Movie(**movie_data.model_dump())
    movie = await MovieService.update_movie(movie_id, updated_movie, db)
    if movie is None:
        raise MovieNotFoundException(movie_id)
    return movie


@router.delete(
    "/{movie_id}",
    response_model={},
    summary="Delete a movie (v1)",
    description="Delete a movie from the database by its ID in version 1.",
    responses={404: {"description": "Movie not found"}},
)
async def delete_movie(
    movie_id: int, db: AsyncSession = Depends(get_db), _user=Depends(get_current_user)
):
    """
    Delete a movie from the database by its ID in version 1.

    Args:
        movie_id (int): The unique ID of the movie to be deleted.
        db (AsyncSession): The database session.

    Returns:
        Movie: The deleted movie object if found.

    Raises:
        HTTPException: If the movie with the specified ID is not found, raises a 404 error.
        :param _user:
        :param movie_id:
        :param db:
    """
    movie = await MovieService.delete_movie(movie_id, db)
    if movie is None:
        raise MovieNotFoundException(movie_id)
    return {"message": "Movie deleted successfully"}

async def get_currency(
    language: Annotated[resolve_accept_language, Depends()],
):
    currencies = {
        "en_US": "USD",
        "fr_FR": "EUR",
    }

    return currencies[language]



@router.get(
    "/i18n/info",
    summary="Get movies api info (v1)",
    description="Get movies api info",
    responses={400: {"description": "invalid parameters"}},
)
@limiter.limit("2/minute")
async def get_info_i18n(
    request: Request,
    background_tasks: BackgroundTasks,
    language: Annotated[resolve_accept_language, Depends()],
    _user=Depends(get_current_user),
):
    """
    Retrieve the content for the internationalization (i18n) of the API.

    Returns:
        dict: The content for i18n.
    """
    info = {
        "en_US": {
            "movies": {"create": "Create a new movie", "get_all": "Get all movies"},
            "movie": {
                "get_by_id": "Get movie by ID",
                "get_by_genre": "Get movies by genre",
                "update": "Update movie by ID",
                "delete": "Delete movie by ID",
            },
        },
        "fr_FR": {
            "movies": {
                "create": "Créer un nouveau film",
                "get_all": "Obtenir tous les films",
            },
            "movie": {
                "get_by_id": "Obtenir le film par ID",
                "get_by_genre": "Obtenir les films par genre",
                "update": "Modifier le film par ID",
                "delete": "Supprimer le film par ID",
            },
        },
    }
    return info[language]


@router.get("/i18n/currency")
@limiter.limit("default_limits")
async def show_currency(
    request: Request,
    background_tasks: BackgroundTasks,
    currency: Annotated[get_currency, Depends()],
    language: Annotated[resolve_accept_language, Depends(use_cache=True)],
    _user=Depends(get_current_user),
):
    currency_name = get_currency_name(currency, locale=language)
    background_tasks.add_task(background_task, currency)
    return {
        "currency": currency,
        "currency_name": currency_name,
    }
