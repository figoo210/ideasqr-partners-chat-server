from sqlalchemy import Boolean, Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config import Base


class ModelActions:
    def as_dict(self):
        # Convert the model instance to a dictionary
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }


class User(Base, ModelActions):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(length=100), unique=True, index=True)
    password = Column(String(length=100))
    name = Column(String(length=100))
    image_url = Column(String(length=2000), nullable=True)
    role_name = Column(String(length=50), ForeignKey("roles.role"), nullable=False)
    disabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    last_modified_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    ip_group_id = Column(String(length=20), ForeignKey("ip_groups.ip"))

    role = relationship("Role", back_populates="users")
    user_chats = relationship("ChatMember", back_populates="user", viewonly=True)
    messages = relationship("Message", back_populates="sender")
    message_reactions = relationship("MessageReaction", back_populates="user")
    ip_group = relationship("IPGroup", back_populates="users")
    reply_shortcuts = relationship(
        "ReplyShortcut", back_populates="user", cascade="all, delete-orphan"
    )


# IP Group model
class IPGroup(Base, ModelActions):
    __tablename__ = "ip_groups"

    ip = Column(String(length=20), primary_key=True, index=True)
    name = Column(String(length=50))

    users = relationship("User", back_populates="ip_group")


class Role(Base, ModelActions):
    __tablename__ = "roles"

    role = Column(String(length=50), primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    last_modified_at = Column(DateTime, default=func.now(), onupdate=func.now())

    users = relationship("User", back_populates="role")
    permissions = relationship(
        "Permission", secondary="role_permissions", viewonly=True
    )


class Permission(Base, ModelActions):
    __tablename__ = "permissions"

    permission = Column(String(length=50), primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    last_modified_at = Column(DateTime, default=func.now(), onupdate=func.now())

    roles = relationship("Role", secondary="role_permissions", viewonly=True)


class RolePermission(Base, ModelActions):
    __tablename__ = "role_permissions"

    role = Column(
        String(length=50), ForeignKey("roles.role"), primary_key=True, index=True
    )
    permission = Column(
        String(length=50),
        ForeignKey("permissions.permission"),
        primary_key=True,
        index=True,
    )


class Chat(Base, ModelActions):
    __tablename__ = "chats"

    chat_name = Column(String(length=50), primary_key=True, index=True)
    image_url = Column(String(length=2000), nullable=True)
    is_group = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    last_modified_at = Column(DateTime, default=func.now(), onupdate=func.now())

    messages = relationship("Message", back_populates="chat")
    chat_members = relationship("ChatMember", back_populates="chat", viewonly=True)


class ChatMember(Base, ModelActions):
    __tablename__ = "chat_members"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(
        String(length=50), ForeignKey("chats.chat_name"), nullable=False, index=True
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    joined_at = Column(DateTime, default=func.now())
    last_modified_at = Column(DateTime, default=func.now(), onupdate=func.now())

    chat = relationship("Chat", backref="members")
    user = relationship("User", backref="chats")


class Message(Base, ModelActions):
    __tablename__ = "messages"

    id = Column(String(length=64), primary_key=True, index=True)
    chat_sequance = Column(Integer, index=True)
    parent_message_id = Column(String(length=64), nullable=True, default=0)
    chat_id = Column(
        String(length=50), ForeignKey("chats.chat_name"), nullable=False, index=True
    )
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=func.now())
    message = Column(String(length=5000))
    seen = Column(Boolean, default=False)
    is_file = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now(), index=True)
    last_modified_at = Column(DateTime, default=func.now(), onupdate=func.now())

    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", back_populates="messages")
    reactions = relationship("MessageReaction", back_populates="message")


class MessageReaction(Base, ModelActions):
    __tablename__ = "message_reactions"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(length=64), ForeignKey("messages.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    reaction = Column(String(length=50))
    created_at = Column(DateTime, default=func.now())
    last_modified_at = Column(DateTime, default=func.now(), onupdate=func.now())

    message = relationship("Message", back_populates="reactions")
    user = relationship("User", back_populates="message_reactions")


class ReplyShortcut(Base):
    __tablename__ = "reply_shortcuts"

    id = Column(Integer, primary_key=True, index=True)
    shortcut = Column(String(255), index=True)
    reply = Column(String(length=5000), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)

    # Define a relationship with the User model
    user = relationship("User", back_populates="reply_shortcuts")
