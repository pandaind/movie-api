from pydantic import BaseModel
from sqlalchemy import Column, Integer, String

from app.db.database import Base


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    genre = Column(String, index=True)
    director = Column(String, index=True)
    release_year = Column(Integer)

    def __repr__(self):
        return f"<Movie title={self.title}, director={self.director}, year={self.release_year}>"

# Pydantic model for serialization/validation
class MovieSchema(BaseModel):
    id: int
    title: str
    genre: str
    director: str
    release_year: int

    model_config = {
        "from_attributes": True  # Allows SQLAlchemy models to be converted to Pydantic models
    }

class CreateMovie(BaseModel):
    title: str
    genre: str
    director: str
    release_year: int
    model_config = {
        "from_attributes": True  # Allows SQLAlchemy models to be converted to Pydantic models
    }