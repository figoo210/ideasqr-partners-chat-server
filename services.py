from typing import Optional
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from models import User, ReplyShortcut
from config import ALGORITHM, SECRET_KEY, get_db, pwd_context, oauth2_scheme
from datetime import datetime, timedelta
import jwt


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(email: str, db: Session = Depends(get_db)):
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db, email: str, password: str):
    user = get_user(email, db)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user



def create_default_reply_shortcuts(user):
    default_shortcuts = [
        ("Ctrl+1", ""),
        ("Ctrl+2", ""),
        ("Ctrl+3", ""),
        ("Ctrl+4", ""),
        ("Ctrl+5", ""),
        ("Ctrl+6", ""),
        ("Ctrl+7", ""),
        ("Ctrl+8", ""),
        ("Ctrl+9", ""),
    ]

    default_reply_shortcuts = [ReplyShortcut(shortcut=shortcut, reply=reply, user=user) for shortcut, reply in default_shortcuts]

    return default_reply_shortcuts


def ensure_default_reply_shortcuts_for_all_users(db):
    users = db.query(User).all()
    for user in users:
        # Check if the user has no reply shortcuts
        if not user.reply_shortcuts:
            # If no reply shortcuts, create and associate the default reply shortcuts
            default_reply_shortcuts = create_default_reply_shortcuts(user)
            user.reply_shortcuts = default_reply_shortcuts

    db.commit()
