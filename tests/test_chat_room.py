import json
import pytest
import websockets
from websockets import serve

from tests.conftests import test_client

async def mock_chatroom(websocket):
    async for message in websocket:
        data = json.loads(message)
        response = {
            "sender": "testuser",
            "message": data["message"]
        }
        await websocket.send(json.dumps(response))
        # Simulate user disconnect
        await websocket.close()

@pytest.mark.asyncio
async def test_chatroom_endpoint(test_client):
    username = "testuser"
    uri = f"ws://localhost:8000/room/{username}"

    async with serve(mock_chatroom, "localhost", 8000):
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps({"message": "Hello, World!"}))
            response = json.loads(await websocket.recv())
            assert response["sender"] == username
            assert response["message"] == "Hello, World!"

            # Simulate user disconnect
            await websocket.close()