from unittest.mock import AsyncMock

import pytest

from app.models.user_role import UserCreateResponse
from tests.conftests import test_client


@pytest.mark.asyncio
async def test_register_user(mocker, test_client):
    mock_user_service = mocker.patch(
        "app.services.user_services.UserService.create_user", new_callable=AsyncMock
    )
    mock_user_service.return_value = UserCreateResponse(
        username="testuser", email="test@example.com"
    )

    response = await test_client.post(
        "/v1/users/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "role": "basic",
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "message": "user created",
        "user": {"username": "testuser", "email": "test@example.com"},
    }


@pytest.mark.asyncio
async def test_register_user_already_exists(mocker, test_client):
    mock_user_service = mocker.patch(
        "app.services.user_services.UserService.create_user", new_callable=AsyncMock
    )
    mock_user_service.return_value = None

    response = await test_client.post(
        "/v1/users/register",
        json={
            "username": "existinguser",
            "email": "existing@example.com",
            "password": "password123",
            "role": "basic",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "username or email already exists",
        "error": "HTTPException occurred",
    }
