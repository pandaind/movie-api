from typing import List

import strawberry
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from app.db.database import get_db
from app.services.movies_services import MovieService


@strawberry.type
class Movie:
    id: int
    title: str
    genre: str
    director: str
    release_year: int


async def get_context(db: AsyncSession = Depends(get_db)):
    return {"db": db}


@strawberry.type
class Query:
    @strawberry.field
    async def movies(self, info: Info) -> List[Movie]:
        db: AsyncSession = info.context["db"]
        movies = await MovieService.get_all_movies(db)
        return [
            Movie(
                id=movie.id,
                title=movie.title,
                genre=movie.genre,
                director=movie.director,
                release_year=movie.release_year,
            )
            for movie in movies
        ]


schema = strawberry.Schema(query=Query)

graphql_app = GraphQLRouter(schema, context_getter=get_context)
