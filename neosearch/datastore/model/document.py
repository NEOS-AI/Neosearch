from sqlalchemy import Column, Text, ForeignKey, TIMESTAMP, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from uuid_extensions import uuid7str


Base = declarative_base()

# Define ENUM for the 'kind' field
kind_enum = ENUM('text', 'code', name='kind_enum', create_type=False)


class Document(Base):
    __tablename__ = 'Document'

    id = Column(UUID(as_uuid=True), nullable=False, server_default=uuid7str())
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=True)
    kind = Column(kind_enum, nullable=False, server_default='text')
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=False)

    # Composite primary key
    __table_args__ = (
        PrimaryKeyConstraint('id', 'created_at', name='document_pk'),
    )
