import json
from fastapi import APIRouter, WebSocket, Depends, HTTPException, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from config import get_db
import models, schemas

router = APIRouter()


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def send_dict(self, data: dict):
        for connection in self.active_connections:
            await connection.send_json(data)


manager = ConnectionManager()


@router.websocket("/ws/chats")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    now = datetime.now()
    current_time = now.strftime("%H:%M")

    try:
        while True:
            data = await websocket.receive_json()
            message = schemas.MessageBase(**data)
            db_message = models.Message(
                chat_id=message.chat_id,
                sender_id=message.sender_id,
                parent_message_id=message.parent_message_id,
                timestamp=datetime.now(),
                message=message.message,
                is_audio=message.is_audio or False,
                is_image=message.is_image or False,
                is_file=message.is_file or False,
                created_at=datetime.now(),
                last_modified_at=datetime.now(),
            )
            db.add(db_message)
            db.commit()
            db.refresh(db_message)
            msg = schemas.Message.from_orm(db_message).dict()
            await manager.send_dict(json.dumps(msg, cls=CustomJSONEncoder))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # await manager.broadcast(json.dumps(message))
