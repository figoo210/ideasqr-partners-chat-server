import json
from fastapi import APIRouter, WebSocket, Depends, HTTPException, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from config import get_db, SessionLocal
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


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            print("################################ WebSocket Data: ", data)

            if "type" in data:
                await manager.send_dict(json.dumps(data, cls=CustomJSONEncoder))

            else:
                print("################################ NO TYPE")

    except WebSocketDisconnect:
        print("################### WEBSOCKET DISCONNECT #####################")
        manager.disconnect(websocket)
        # await manager.broadcast(json.dumps(message))
