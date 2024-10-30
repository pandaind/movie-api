from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from app.db.database import Base


class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    books = relationship("Book", back_populates="author")


author = Author(name="J.K. Rowling")