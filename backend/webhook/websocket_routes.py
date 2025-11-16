from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
from services.websocket_service import websocket_service

websocket_router = APIRouter()


@websocket_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, project: Optional[str] = Query(None)):
    """
    WebSocket эндпоинт для реальных уведомлений
    """
    await websocket_service.connect(websocket, project)

    try:
        while True:
            # Получаем сообщение от клиента (ping)
            data = await websocket.receive_text()

            # Отправляем pong в ответ
            await websocket_service.send_personal_message({
                "type": "pong",
                "message": "pong",
                "timestamp": data
            }, websocket)

    except WebSocketDisconnect:
        websocket_service.disconnect(websocket, project)
    except Exception as e:
        websocket_service.disconnect(websocket, project)