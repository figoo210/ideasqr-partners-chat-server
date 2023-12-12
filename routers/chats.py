from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_
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
def get_chats(db: Session = Depends(get_db)):
    chats = db.query(models.Chat).all()
    return chats


@router.get("/group-chats/", response_model=List[schemas.Chat])
def get_group_chats(request: Request, db: Session = Depends(get_db)):
    user_id = request.headers.get("user_id")
    chats = db.query(models.Chat).filter(
        models.Chat.is_group == True,
        models.Chat.chat_members.any(models.ChatMember.user_id == user_id)
    ).all()
    return chats


@router.get("/direct-chats/", response_model=List[schemas.Chat])
def get_direct_chats(request: Request, db: Session = Depends(get_db)):
    user_id = request.headers.get("user_id")
    chats = db.query(models.Chat).filter(
        models.Chat.is_group == False,
        or_(models.Chat.chat_name.like(f"%-{user_id}-%"), models.Chat.chat_name.like(f"%-{user_id}"))
    ).all()
    return chats


@router.get("/chats/{chat_name}", response_model=schemas.Chat)
def get_chat(chat_name: str, db: Session = Depends(get_db)):
    chat = db.query(models.Chat).filter(models.Chat.chat_name == chat_name).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    chat.messages = db.query(models.Message).filter_by(chat_id=chat.chat_name).order_by(models.Message.created_at.desc()).limit(100).all()
    return chat


@router.get("/chats/check/{chat_name}")
def check_group_name(chat_name: str, db: Session = Depends(get_db)):
    chat = db.query(models.Chat).filter(models.Chat.chat_name == chat_name).first()
    if not chat:
        return {"is_exist": False}
    else:
        return {"is_exist": True}


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


@router.post("/update-chat-members")
def update_chat_members(request: schemas.ChatMemberUpdate, db: Session = Depends(get_db)):
    try:
        chat = db.query(models.Chat).filter_by(chat_name=request.chat_id).first()

        if chat:
            # Delete members not in the new list
            db.query(models.ChatMember).filter(models.ChatMember.chat_id == chat.chat_name, ~models.ChatMember.user_id.in_(request.user_ids)).delete(synchronize_session=False)

            # Add new members
            for user_id in request.user_ids:
                user = db.query(models.User).filter_by(id=user_id).first()

                if user:
                    # Check if the user is not already a member
                    existing_member = db.query(models.ChatMember).filter_by(chat_id=chat.chat_name, user_id=user.id).first()
                    if not existing_member:
                        chat_member = models.ChatMember(chat_id=chat.chat_name, user_id=user.id, joined_at=datetime.now())
                        db.add(chat_member)
            db.commit()
            return {"message": "Chat members updated successfully.", "chat_members": chat.chat_members}
        else:
            raise HTTPException(status_code=404, detail="Chat not found.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
