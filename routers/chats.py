from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from config import get_db
import models, schemas

router = APIRouter()

# Chat Endpoints


@router.post("/chats/", response_model=schemas.Chat)
def create_chat(chat: schemas.ChatCreate, db: Session = Depends(get_db)):
    db_chat = models.Chat(
        chat_name=chat.chat_name,
        image_url=chat.image_url,
        is_group=chat.is_group,
        created_at=datetime.now(),
        last_modified_at=datetime.now(),
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    if db_chat.is_group:
        if len(chat.members) > 0:
            for each_member in chat.members:
                new_member = models.ChatMember(
                    chat_id=chat.chat_name,
                    user_id=int(each_member),
                    joined_at=datetime.now(),
                    last_modified_at=datetime.now(),
                )
                db.add(new_member)
                db.commit()
                db.refresh(new_member)

    return db_chat


@router.get("/chats/", response_model=List[schemas.Chat])
def get_chats(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    chats = db.query(models.Chat).offset(skip).limit(limit).all()
    return chats


@router.get("/chats/{chat_name}", response_model=schemas.Chat)
def get_chat(chat_name: str, db: Session = Depends(get_db)):
    chat = db.query(models.Chat).filter(models.Chat.chat_name == chat_name).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.put("/chats/{chat_name}", response_model=schemas.Chat)
def update_chat(
    chat_name: str, chat: schemas.ChatUpdate, db: Session = Depends(get_db)
):
    db_chat = db.query(models.Chat).filter(models.Chat.chat_name == chat_name).first()
    if not db_chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    db_chat.chat_name = chat.chat_name
    db_chat.image_url = chat.image_url
    db_chat.is_group = chat.is_group
    db_chat.last_modified_at = datetime.now()
    db.commit()
    db.refresh(db_chat)
    return db_chat


@router.delete("/chats/{chat_name}")
def delete_chat(chat_name: str, db: Session = Depends(get_db)):
    db_chat = db.query(models.Chat).filter(models.Chat.chat_name == chat_name).first()
    if not db_chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    db.delete(db_chat)
    db.commit()
    return {"message": "Chat deleted"}
