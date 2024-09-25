from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.movie import Base

DATABASE_URL = settings.database_url

# Create Async Engine for PostgreSQL
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a sessionmaker for async ORM
async_session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession  # AsyncSession for non-blocking I/O
)

# Initialize database models
async def init_db():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

# Dependency to get the session
async def get_db():
    async with async_session() as session:
        yield session
