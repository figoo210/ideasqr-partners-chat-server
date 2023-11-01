from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import requests

import models, schemas
from config import ACCESS_TOKEN_EXPIRE_MINUTES, get_db
from services import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
)

router = APIRouter()


# User Endpoints


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    forwarded_for = request.headers.get("X-User-IP")
    if forwarded_for:
        user_ip = forwarded_for
    else:
        user_ip = request.client.host
    print("################################# user_ip: ", user_ip)

    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect Email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.ip_group_id and len(user.ip_group_id) > 0:
        if user.ip_group_id != user_ip:
            raise HTTPException(
                status_code=401,
                detail="You are logging in from unallowed IP.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    role = db.query(models.Role).filter(models.Role.role == user.role_name).first()
    resp = {
        "access_token": access_token,
        "token_type": "bearer",
        "data": user,
        "role": role,
    }
    return resp


@router.get("/users/me/{id}", response_model=schemas.Token)
async def read_users_me(id: str, db: Session = Depends(get_db)):
    current_user = db.quiry(models.User).filter(models.User.id == id).first()
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.email}, expires_delta=access_token_expires
    )

    role = (
        db.query(models.Role).filter(models.Role.role == current_user.role_name).first()
    )
    resp = {
        "access_token": access_token,
        "token_type": "bearer",
        "data": current_user,
        "role": role,
    }
    return resp


@router.post("/users", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(**user.dict())
    db_user.password = get_password_hash(db_user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/users/{id}", response_model=schemas.User)
async def read_user(id: str, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get("/users/", response_model=List[schemas.User])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.email = user.email if len(user.email) > 0 else db_user.email
    db_user.password = (
        get_password_hash(user.password) if len(user.password) > 0 else db_user.password
    )
    db_user.name = user.name if len(user.name) > 0 else db_user.name
    db_user.image_url = user.image_url if len(user.image_url) > 0 else db_user.image_url
    db_user.role_name = user.role_name if len(user.role_name) > 0 else db_user.role_name
    db_user.last_modified_at = datetime.now()
    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted"}
