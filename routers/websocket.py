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
        if isinstance(obj.__class__, models.MessageReaction):
            # If the object is a SQLAlchemy ORM object, convert it to a dictionary
            return obj.__dict__
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
            try:
                await connection.send_json(data)
            except WebSocketDisconnect as e:
                print("############################## E: ", e)
                self.active_connections.remove(connection)


manager = ConnectionManager()


@router.websocket("/ws/chats")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            print("################################ Chats Data: ", data)
            if "reaction" in data:
                await manager.send_dict(json.dumps({"reaction": data["reaction"], "chat_id": data["chat_id"]}, cls=CustomJSONEncoder))
            elif "edit" in data:
                response = {
                    **data["edit"],
                    "edit": "edit"
                }
                await manager.send_dict(json.dumps(response, cls=CustomJSONEncoder))
            else:
                message = schemas.MessageBase(**data)
                db_message = models.Message(
                    chat_id=message.chat_id,
                    sender_id=message.sender_id,
                    parent_message_id=message.parent_message_id,
                    timestamp=datetime.now(),
                    message=message.message,
                    seen=message.seen or False,
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
        print("################### Chats DISCONNECT #####################")
        manager.disconnect(websocket)
        # await manager.broadcast(json.dumps(message))


@router.websocket("/ws/calls")
async def websocket_endpoint_calls(websocket: WebSocket, db: Session = Depends(get_db)):
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            print("################################ Calls Data: ", data)
            await manager.send_dict(json.dumps(data, cls=CustomJSONEncoder))

    except WebSocketDisconnect:
        print("################### Calls DISCONNECT #####################")
        manager.disconnect(websocket)
        # await manager.broadcast(json.dumps(message))
