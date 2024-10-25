from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.user_role import Role, User
from tests.conftests import common_mocks

client = TestClient(app)

mock_basic_user = User(username="testuser", role=Role.basic)
mock_premium_user = User(username="premiumuser", role=Role.premium)


@pytest.mark.asyncio
@patch(
    "app.security.security.decode_access_token",
    new_callable=AsyncMock,
    return_value=mock_basic_user,
)
async def test_read_user_me_success(mocker):
    response = client.get(
        "/v1/security/users/me", headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 200
    assert response.json() == {"description": "testuser authorized"}


@pytest.mark.asyncio
@patch(
    "app.security.security.decode_access_token",
    new_callable=AsyncMock,
    return_value=None,
)
async def test_read_user_me_unauthorized(mocker):
    response = client.get(
        "/v1/security/users/me", headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401
    assert response.json() == {
        "detail": "User not authorized",
        "error": "HTTPException occurred",
    }


@pytest.mark.asyncio
@patch(
    "app.security.security.decode_access_token",
    new_callable=AsyncMock,
    return_value=mock_premium_user,
)
async def test_read_user_premium_success(mocker):
    response = client.get(
        "/v1/security/users/premium", headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 200
    assert response.json() == {"description": "premiumuser authorized"}


@pytest.mark.asyncio
@patch(
    "app.security.security.decode_access_token",
    new_callable=AsyncMock,
    return_value=None,
)
async def test_read_user_premium_unauthorized(mocker):
    response = client.get(
        "/v1/security/users/premium", headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401
    assert response.json() == {
        "detail": "User not authorized",
        "error": "HTTPException occurred",
    }


@pytest.mark.asyncio
async def test_get_user_access_token_success(mocker):
    mock_user = User(username="testuser", role=Role.basic)
    mocker.patch("app.security.api.authenticate_user", return_value=mock_user)
    mocker.patch("app.security.api.create_access_token", return_value="testtoken")
    response = client.post(
        "/v1/security/token", data={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 200
    assert response.json() == {"access_token": "testtoken", "token_type": "bearer"}


@pytest.mark.asyncio
async def test_get_user_access_token_unauthorized(mocker):
    mocker.patch("app.security.api.authenticate_user", return_value=None)
    response = client.post(
        "/v1/security/token",
        data={"username": "invaliduser", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Incorrect username or password",
        "error": "HTTPException occurred",
    }
