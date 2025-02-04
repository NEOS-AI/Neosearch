from sqlalchemy import Column, String, JSON, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from uuid_extensions import uuid7str

# custom modules
from .base import Base


class Message(Base):
    __tablename__ = 'Message'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=uuid7str(), nullable=False)
    chat_id = Column(UUID(as_uuid=True), ForeignKey('Chat.id'), nullable=False)
    role = Column(String, nullable=False)
    content = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<Message(id={self.id}, chat_id={self.chat_id}, role={self.role}, content={self.content}, created_at={self.created_at})>"
