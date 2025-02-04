from sqlalchemy import Column, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.sql import func

# custom modules
from .base import Base


visibility_enum = ENUM('public', 'private', name='visibility_enum', create_type=False)

class Chat(Base):
    __tablename__ = 'Chat'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        nullable=False,
    )
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    title = Column(Text, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('User.id'), nullable=False)
    visibility = Column(
        visibility_enum,
        nullable=False,
        server_default="private"
    )
