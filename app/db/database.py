from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

DATABASE_URL = settings.database_url

Base = declarative_base()

# Create Async Engine for PostgreSQL
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a sessionmaker for async ORM
async_session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,  # AsyncSession for non-blocking I/O
)


# Initialize database models
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Dependency to get the session
async def get_db():
    async with async_session() as session:
        yield session
