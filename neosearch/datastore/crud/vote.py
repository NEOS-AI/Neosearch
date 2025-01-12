from sqlalchemy.orm import Session
from uuid import UUID

# custom modules
from neosearch.datastore.model.vote import Vote


class VoteCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create_vote(self, chat_id: UUID, message_id: UUID, is_upvoted: bool):
        """Create a new vote."""
        new_vote = Vote(
            chat_id=chat_id,
            message_id=message_id,
            is_upvoted=is_upvoted,
        )
        self.session.add(new_vote)
        self.session.commit()
        return new_vote

    def get_vote(self, chat_id: UUID, message_id: UUID):
        """Retrieve a vote by its composite key (chat_id and message_id)."""
        return (
            self.session.query(Vote)
            .filter_by(chat_id=chat_id, message_id=message_id)
            .one_or_none()
        )

    def get_votes_by_chat(self, chat_id: UUID):
        """Retrieve all votes for a specific chat."""
        return self.session.query(Vote).filter_by(chat_id=chat_id).all()

    def update_vote(self, chat_id: UUID, message_id: UUID, is_upvoted: bool):
        """Update a vote's is_upvoted value."""
        vote = self.get_vote(chat_id, message_id)
        if vote:
            vote.is_upvoted = is_upvoted
            self.session.commit()
        return vote

    def delete_vote(self, chat_id: UUID, message_id: UUID):
        """Delete a vote by its composite key."""
        vote = self.get_vote(chat_id, message_id)
        if vote:
            self.session.delete(vote)
            self.session.commit()
            return True
        return False
