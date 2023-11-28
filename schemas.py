from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime



class ReplyShortcut(BaseModel):
    id: Optional[int] = None
    shortcut: Optional[str] = None
    reply: Optional[str] = None


class ReplyShortcutList(BaseModel):
    shortcuts: List[ReplyShortcut]


class UserBase(BaseModel):
    email: str
    name: str
    ip_group_id: Optional[str] = None


class UserCreate(UserBase):
    password: str
    role_name: str
    image_url: Optional[str] = None


class User(UserBase):
    id: int
    image_url: Optional[str] = None
    role_name: str
    disabled: bool
    created_at: datetime
    last_modified_at: datetime
    image_url: Optional[str] = None
    reply_shortcuts: Optional[List[ReplyShortcut]] = None


class TokenData(BaseModel):
    email: Optional[str] = None


class IPGroupBase(BaseModel):
    ip: str
    name: str
    users: Optional[List[int]] = None


class RoleBase(BaseModel):
    role: str


class RoleCreate(RoleBase):
    pass


class PermissionBase(BaseModel):
    permission: str


class PermissionCreate(PermissionBase):
    pass


class Permission(PermissionBase):
    permission: str
    created_at: datetime
    last_modified_at: datetime


class Role(RoleBase):
    role: str
    created_at: datetime
    last_modified_at: datetime
    permissions: Optional[List[Permission]] = None


class Token(BaseModel):
    access_token: str
    token_type: str
    data: User
    role: Role


class RolePermission(BaseModel):
    role: str
    permissions: List[str]


class RolePermissionResponse(BaseModel):
    roles_permissions: List[RolePermission]


class ChatBase(BaseModel):
    chat_name: str
    image_url: Optional[str] = None
    is_group: bool


class ChatCreate(ChatBase):
    members: Optional[List[int]] = None


class ChatMemberBase(BaseModel):
    chat_id: str
    user_id: int


class ChatMemberCreate(ChatMemberBase):
    pass


class ChatMemberUpdate(BaseModel):
    chat_id: Optional[str]
    user_ids: Optional[List[int]]


class ChatMemberResponse(BaseModel):
    id: int
    chat_id: str
    user_id: int
    joined_at: Optional[datetime]
    last_modified_at: Optional[datetime]


class ChatMembersResponse(BaseModel):
    chat_members: List[ChatMemberResponse]


class MessageBase(BaseModel):
    chat_id: str
    sender_id: int
    parent_message_id: Optional[int] = None
    timestamp: Optional[datetime] = None
    message: str
    seen: Optional[bool] = None
    is_file: Optional[bool] = None


class MessageReactionBase(BaseModel):
    message_id: int
    user_id: int
    reaction: str


class MessageReactionCreate(MessageReactionBase):
    pass


class MessageReaction(MessageReactionBase):
    id: int
    created_at: datetime
    last_modified_at: datetime

    class Config:
        from_attributes = True


class Message(MessageBase):
    id: int
    created_at: datetime
    last_modified_at: datetime
    reactions: Optional[List[MessageReaction]]

    class Config:
        from_attributes = True


class Chat(ChatBase):
    chat_name: str
    messages: Optional[List[Message]] = None
    chat_members: Optional[List[ChatMemberResponse]] = None
    created_at: datetime
    last_modified_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(UserBase):
    password: Optional[str] = None
    role_name: Optional[str] = None
    image_url: Optional[str] = None


class RoleUpdate(RoleBase):
    role: str


class PermissionUpdate(PermissionBase):
    permission: str


class ChatUpdate(ChatBase):
    chat_name: str


class MessageUpdate(MessageBase):
    pass


class MessageReactionUpdate(MessageReactionBase):
    id: int
