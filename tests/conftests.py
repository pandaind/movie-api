import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from passlib.context import CryptContext
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.profiler import ProfileEndpointsMiddleWare
from app.db.database import Base, get_db
from app.main import app
from app.models.user_role import User, UserRole


async def side_effect_profile_endpoint_middleware(request, call_next):
    return await call_next(request)


@pytest.fixture(scope="function")
def common_mocks(mocker):
    mocker.patch(
        "app.security.security.decode_access_token",
        return_value={"user_id": 1, "username": "testuser", "role": "basic"},
    )

    yield
    mocker.stopall()


engine = create_async_engine(
    "sqlite+aiosqlite:///./test.db",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    await init_models()
    yield
    await drop_models()


TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


@pytest_asyncio.fixture(scope="function")
async def test_db_session(setup_db):
    async with TestingSessionLocal() as session:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash("hello")
        default_user = User(
            username="pandaind",
            email="pandaind@example.com",
            hashed_password=hashed_password,
            role=UserRole.basic,
            totp_secret="",
        )
        session.add(default_user)
        await session.commit()
        yield session


@pytest_asyncio.fixture(scope="function")
async def integration_test_client(test_db_session, mocker):
    mocker.patch.object(
        ProfileEndpointsMiddleWare,
        "dispatch",
        side_effect=side_effect_profile_endpoint_middleware,
    )
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        yield client


@pytest_asyncio.fixture(scope="function")
async def test_client(mocker):
    mocker.patch.object(
        ProfileEndpointsMiddleWare,
        "dispatch",
        side_effect=side_effect_profile_endpoint_middleware,
    )
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client
