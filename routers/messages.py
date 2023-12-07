from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from config import get_db
import models, schemas

router = APIRouter()

# Message Endpoints


@router.post("/messages/", response_model=schemas.Message)
def create_message(message: schemas.MessageBase, db: Session = Depends(get_db)):
    chat_sequance = 1

    last_message = (
        db.query(models.Message)
        .filter(models.Message.chat_id == message.chat_id)
        .order_by(models.Message.created_at.desc())
        .first()
    )

    if last_message:
        chat_sequance = last_message.chat_sequance + 1

    db_message = models.Message(
        id=message.id,
        chat_sequance=chat_sequance,
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
    return db_message


@router.get("/messages/", response_model=List[schemas.Message])
def get_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    messages = db.query(models.Message).offset(skip).limit(limit).all()
    return messages


@router.get("/chat/messages/{chat_id}", response_model=List[schemas.Message])
def get_message(chat_id: str, db: Session = Depends(get_db)):
    messages = db.query(models.Message).filter(models.Message.chat_id == chat_id).all()
    if not messages or len(messages) == 0:
        raise HTTPException(status_code=404, detail="Message not found")
    return messages


@router.put("/messages/{message_id}", response_model=schemas.Message)
def update_message(
    message_id: str, message: schemas.MessageUpdate, db: Session = Depends(get_db)
):
    db_message = (
        db.query(models.Message).filter(models.Message.id == message_id).first()
    )
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    db_message.chat_id = message.chat_id
    db_message.sender_id = message.sender_id
    db_message.timestamp = datetime.now()
    db_message.message = message.message
    db_message.seen = message.seen
    db_message.is_file = message.is_file
    db_message.last_modified_at = datetime.now()
    db.commit()
    db.refresh(db_message)
    return db_message


@router.delete("/messages/{message_id}")
def delete_message(message_id: str, db: Session = Depends(get_db)):
    db_message = (
        db.query(models.Message).filter(models.Message.id == message_id).first()
    )
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(db_message)
    db.commit()
    return {"message": "Message deleted"}


@router.get("/messages/{message_id}")
def seen_message(message_id: str, db: Session = Depends(get_db)):
    db_message = (
        db.query(models.Message).filter(models.Message.id == message_id).first()
    )
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    db_message.seen = True
    db.commit()
    db.refresh(db_message)
    return {"message": "Message Seen"}
