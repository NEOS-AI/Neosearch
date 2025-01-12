from sqlalchemy.orm import Session
from uuid import UUID

# custom modules
from neosearch.datastore.model.document import Document


class DocumentCRUD:
    def __init__(self, session: Session):
        self.session = session

    def create_document(self, title: str, kind: str, user_id: UUID, content: str = None):
        """Create a new document."""
        new_document = Document(
            title=title,
            content=content,
            kind=kind,
            user_id=user_id,
        )
        self.session.add(new_document)
        self.session.commit()
        self.session.refresh(new_document)
        return new_document

    def get_document(self, doc_id: UUID, created_at: str):
        """Retrieve a document by its composite key (id and created_at)."""
        return (
            self.session.query(Document)
            .filter_by(id=doc_id, created_at=created_at)
            .one_or_none()
        )

    def get_documents_by_user(self, user_id: UUID, kind: str = None):
        """Retrieve all documents for a specific user, optionally filtered by kind."""
        query = self.session.query(Document).filter_by(user_id=user_id)
        if kind:
            query = query.filter_by(kind=kind)
        return query.all()

    def update_document(self, doc_id: UUID, created_at: str, **kwargs):
        """Update a document by its composite key."""
        doc = self.get_document(doc_id, created_at)
        if doc:
            for key, value in kwargs.items():
                setattr(doc, key, value)
            self.session.commit()
        return doc

    def delete_document(self, doc_id: UUID, created_at: str):
        """Delete a document by its composite key."""
        doc = self.get_document(doc_id, created_at)
        if doc:
            self.session.delete(doc)
            self.session.commit()
            return True
        return False
