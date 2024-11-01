import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Request,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
)
from fastapi.responses import HTMLResponse
from starlette import status

from app.chat.template import templates
from app.chat.web_socket_manger import ConnectionManager
from app.chat.ws_security import get_username_from_token

conn_manager = ConnectionManager()
logger = logging.getLogger("uvicorn")


router = APIRouter()


@router.websocket("/room/{username}")
async def chatroom_endpoint(websocket: WebSocket, username: str):
    await conn_manager.connect(websocket)
    await conn_manager.broadcast(
        {
            "sender": "system",
            "message": f"{username} joined the chat",
        },
        exclude=websocket,
    )

    logger.info(f"{username} joined the chat")

    try:
        while True:
            data = await websocket.receive_text()
            await conn_manager.broadcast(
                {"sender": username, "message": data},
                exclude=websocket,
            )
            await conn_manager.send_personal_message(
                {"sender": "You", "message": data},
                websocket,
            )
            logger.info(f"{username} says: {data}")
    except WebSocketDisconnect:
        conn_manager.disconnect(websocket)
        await conn_manager.broadcast(
            {
                "sender": "system",
                "message": f"{username} " "left the chat",
            }
        )
        logger.info(f"{username} left the chat")


@router.get("/page/{username}")
async def chatroom_page_endpoint(request: Request, username: str) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="chatroom.html",
        context={"username": username},
    )


@router.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Welcome to the chat room!")
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Message received: {data}")
            await websocket.send_text("Message received!")
            if data == "disconnect":
                logger.warning("Disconnecting...")
                return await websocket.close(
                    code=status.WS_1000_NORMAL_CLOSURE,
                    reason="Disconnecting...",
                )
            if "bad message" in data:
                raise WebSocketException(
                    code=status.WS_1008_POLICY_VIOLATION,
                    reason="Inappropriate message",
                )
    except WebSocketDisconnect:
        logger.warning("Connection closed by the client")


@router.websocket("/secured-ws")
async def secured_websocket(
    websocket: WebSocket,
    username: Annotated[get_username_from_token, Depends()],
):
    await websocket.accept()
    await websocket.send_text(f"Welcome {username}!")
    async for data in websocket.iter_text():
        await websocket.send_text(f"You wrote: {data}")
