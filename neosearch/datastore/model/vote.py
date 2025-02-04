from sqlalchemy import Column, Boolean, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID

# custom modules
from .base import Base


class Vote(Base):
    __tablename__ = 'Vote'

    chat_id = Column(UUID(as_uuid=True), ForeignKey('Chat.id'), nullable=False)
    message_id = Column(UUID(as_uuid=True), ForeignKey('Message.id'), nullable=False)
    is_upvoted = Column(Boolean, nullable=False)

    # Composite primary key
    __table_args__ = (
        PrimaryKeyConstraint('chat_id', 'message_id', name='vote_pk'),
    )
