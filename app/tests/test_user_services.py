import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.orm import joinedload, load_only

from app.models.user_role import User, Profile
from app.services.user_services import UserService


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.mark.asyncio
async def test_get_user_with_profile(mock_session):
    user_id = 1
    mock_user = User(id=user_id, username="testuser", email="test@example.com")
    mock_user.profile = Profile(bio="Test bio")

    # mock_session.execute is an AsyncMock, so its return_value is what 'await session.execute' gives.
    # This return_value then needs a scalar_one_or_none method.
    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute = AsyncMock(return_value=mock_execute_result)

    user = await UserService.get_user_with_profile(mock_session, user_id)

    assert user is not None
    assert user.id == user_id
    assert user.profile is not None
    assert user.profile.bio == "Test bio"
    mock_session.execute.assert_called_once()
    call_args = mock_session.execute.call_args[0][0]
    assert str(call_args) == str(
        select(User).options(joinedload(User.profile)).where(User.id == user_id)
    )


@pytest.mark.asyncio
async def test_get_user_with_profile_join(mock_session):
    user_id = 1
    mock_user = User(id=user_id, username="testuser", email="test@example.com")
    # For this test, the profile object might not be fully loaded due to load_only
    # We are primarily testing the query construction
    mock_user.profile = Profile(id=1)

    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute = AsyncMock(return_value=mock_execute_result)

    user = await UserService.get_user_with_profile_join(mock_session, user_id)

    assert user is not None
    assert user.id == user_id
    # Depending on how SQLAlchemy handles load_only with joined relationships,
    # user.profile might be a placeholder or partially loaded.
    # The key is to check the query.
    mock_session.execute.assert_called_once()
    call_args = mock_session.execute.call_args[0][0]
    expected_stmt = (
        select(User)
        .join(User.profile)
            .options(load_only(User.username, User.email))  # User.profile removed
        .where(User.id == user_id)
    )
    assert str(call_args) == str(expected_stmt)


@pytest.mark.asyncio
async def test_get_user_with_ony_bio(mock_session):
    user_id = 1
    mock_user = User(id=user_id, username="testuser", email="test@example.com")
    mock_user.profile = Profile(bio="Only bio")

    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute = AsyncMock(return_value=mock_execute_result)

    user = await UserService.get_user_with_ony_bio(mock_session, user_id)

    assert user is not None
    assert user.id == user_id
    assert user.profile is not None
    assert user.profile.bio == "Only bio"
    # Potentially other profile attributes would be unloaded,
    # but we are mocking the return object directly here.
    mock_session.execute.assert_called_once()
    call_args = mock_session.execute.call_args[0][0]
    expected_stmt = (
        select(User)
        .options(joinedload(User.profile).load_only(Profile.bio))
        .where(User.id == user_id)
    )
    assert str(call_args) == str(expected_stmt)


@pytest.mark.asyncio
async def test_get_user_with_options_no_options(mock_session):
    user_id = 1
    mock_user = User(id=user_id, username="testuser")

    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute = AsyncMock(return_value=mock_execute_result)

    user = await UserService._get_user_with_options(mock_session, user_id)

    assert user is not None
    assert user.id == user_id
    mock_session.execute.assert_called_once()
    call_args = mock_session.execute.call_args[0][0]
    assert str(call_args) == str(select(User).where(User.id == user_id))


@pytest.mark.asyncio
async def test_get_user_with_options_with_options(mock_session):
    user_id = 1
    mock_user = User(id=user_id, username="testuser")

    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute = AsyncMock(return_value=mock_execute_result)
    option = joinedload(User.profile)

    user = await UserService._get_user_with_options(mock_session, user_id, option)

    assert user is not None
    assert user.id == user_id
    mock_session.execute.assert_called_once()
    call_args = mock_session.execute.call_args[0][0]
    assert str(call_args) == str(select(User).options(option).where(User.id == user_id))

# To run these tests, you would typically use a command like:
# pytest app/tests/test_user_services.py
# Ensure you have pytest and pytest-asyncio installed:
# pip install pytest pytest-asyncio
# Also, the User and Profile models need to be accessible.
# The import "from app.models.user_role import User, Profile" assumes a certain project structure.
# You might need to adjust imports based on your actual project structure.

# Need to mock select from sqlalchemy
from sqlalchemy import select as real_select
# Mock select to compare query objects
# This is a bit of a hack, ideally we would have a better way to compare sqlalchemy queries
# For now, comparing string representations is a pragmatic approach for these tests.
# We also need to ensure that the select used in the service is the same as the one used in tests.
# So we replace the select in the service with a mock that returns a comparable object.

# In a real scenario, you'd also need to set up your test environment
# to handle async database sessions properly, potentially using a test database.
# The current mocks bypass actual database interaction.

# The User and Profile models would need to be defined for these tests to run.
# Example minimal definitions:
# from sqlalchemy.orm import relationship
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Column, Integer, String, ForeignKey
#
# Base = declarative_base()
#
# class Profile(Base):
#     __tablename__ = "profile"
#     id = Column(Integer, primary_key=True)
#     bio = Column(String)
#     user_id = Column(Integer, ForeignKey("user.id"))
#
# class User(Base):
#     __tablename__ = "user"
#     id = Column(Integer, primary_key=True)
#     username = Column(String)
#     email = Column(String)
#     profile = relationship("Profile", uselist=False, backref="user")

# The above model definitions are just for context if you were to run this standalone.
# In your project, these would come from app.models.user_role
#
# Also, the `select` import in `app.services.user_services` needs to be `sqlalchemy.select`
# and not a local alias if we want to easily mock it or compare its string output.
# For these tests, I'm assuming `from sqlalchemy import select` is used in user_services.py
# and the string comparison of the generated SQL is sufficient.
#
# A more robust way to check options would be to inspect the mock_calls on the query object
# if the query object itself was mocked, but that adds more complexity to the mocking setup.
# Here, we are mocking the session's execute method and inspecting the statement passed to it.
select = real_select # Ensure tests use the real select for constructing expected statements.
