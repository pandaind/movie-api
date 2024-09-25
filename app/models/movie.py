from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    director = Column(String, index=True)
    release_year = Column(Integer)

    def __repr__(self):
        return f"<Movie title={self.title}, director={self.director}, year={self.release_year}>"


# Pydantic model for serialization/validation
class MovieSchema(BaseModel):
    id: int
    title: str
    director: str
    release_year: int

    class Config:
        orm_mode = True  # Allows SQLAlchemy models to be converted to Pydantic models


class CreateMovie(MovieSchema):
    class Config:
        orm_mode = True  # Allows Pydantic models to be converted to SQLAlchemy models