from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from uuid import UUID

# custom modules
from neosearch.datastore.model.chat import Chat


class ChatCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create_chat(self, title: str, user_id: UUID, visibility: str = "private"):
        """Create a new chat."""
        new_chat = Chat(
            title=title,
            user_id=user_id,
            visibility=visibility,
        )
        self.session.add(new_chat)
        self.session.commit()
        self.session.refresh(new_chat)
        return new_chat

    def get_chat_by_id(self, chat_id: UUID):
        """Retrieve a chat by its ID."""
        return self.session.get(Chat, chat_id)

    def get_all_chats(self, user_id: UUID = None, visibility: str = None):
        """Retrieve all chats, optionally filtered by user_id and/or visibility."""
        query = select(Chat)
        if user_id:
            query = query.where(Chat.user_id == user_id)
        if visibility:
            query = query.where(Chat.visibility == visibility)
        return self.session.execute(query).scalars().all()

    def update_chat(self, chat_id: UUID, **kwargs):
        """Update a chat by its ID."""
        stmt = update(Chat).where(Chat.id == chat_id).values(**kwargs)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount  # Returns the number of rows updated

    def delete_chat(self, chat_id: UUID):
        """Delete a chat by its ID."""
        stmt = delete(Chat).where(Chat.id == chat_id)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount  # Returns the number of rows deleted
