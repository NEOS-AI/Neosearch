from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from uuid import UUID

# custom modules
from neosearch.datastore.model.message import Message


class MessageCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create_message(self, chat_id: UUID, role: str, content: dict):
        """Create a new message."""
        new_message = Message(
            chat_id=chat_id,
            role=role,
            content=content,
        )
        self.session.add(new_message)
        self.session.commit()
        self.session.refresh(new_message)
        return new_message

    def get_message_by_id(self, message_id: UUID):
        """Retrieve a message by its ID."""
        return self.session.get(Message, message_id)

    def get_all_messages(self, chat_id: UUID = None):
        """Retrieve all messages, optionally filtered by chat_id."""
        query = select(Message)
        if chat_id:
            query = query.where(Message.chat_id == chat_id)
        return self.session.execute(query).scalars().all()

    def update_message(self, message_id: UUID, **kwargs):
        """Update a message by its ID."""
        stmt = update(Message).where(Message.id == message_id).values(**kwargs)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount  # Returns the number of rows updated

    def delete_message(self, message_id: UUID):
        """Delete a message by its ID."""
        stmt = delete(Message).where(Message.id == message_id)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount  # Returns the number of rows deleted
