"""SQLAlchemy database service for message persistence."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import create_engine, select, update, delete, func
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy import Column, String, Integer, DateTime

Base = declarative_base()


class Message(Base):
    """Message table model."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, nullable=False, unique=True)
    conversation_id = Column(String, nullable=False)
    content = Column(String, nullable=False)
    name = Column(String, nullable=True)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "uuid": self.uuid,
            "conversation_id": self.conversation_id,
            "content": self.content,
            "name": self.name,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DatabaseService:
    """Service for database operations with messages."""

    def __init__(self, db_path: str = "sqlite:///database.db"):
        """Initialize database service.

        Args:
            db_path: Database connection string. Defaults to SQLite database.db.
        """
        self.engine = create_engine(db_path, echo=False)
        Base.metadata.create_all(self.engine)

    async def insert_message(
        self,
        uuid: str,
        conversation_id: str,
        content: str,
        role: str,
        name: Optional[str] = None,
    ) -> dict:
        """Insert a message.

        Args:
            uuid: Message UUID.
            conversation_id: Conversation ID.
            content: Message content.
            role: Message role (user/assistant).
            name: Optional sender name.

        Returns:
            Created message as dictionary.
        """
        with Session(self.engine) as session:
            message = Message(
                uuid=uuid,
                conversation_id=conversation_id,
                content=content,
                role=role,
                name=name,
            )
            session.add(message)
            session.commit()
            session.refresh(message)
            return message.to_dict()

    async def get_messages_by_conversation_id(
        self,
        conversation_id: str,
    ) -> List[dict]:
        """Get messages by conversation ID.

        Args:
            conversation_id: Conversation ID.

        Returns:
            List of messages.
        """
        with Session(self.engine) as session:
            stmt = select(Message).where(
                Message.conversation_id == conversation_id
            )
            messages = session.scalars(stmt).all()
            return [msg.to_dict() for msg in messages]

    async def get_message_by_uuid(self, uuid: str) -> Optional[dict]:
        """Get message by UUID.

        Args:
            uuid: Message UUID.

        Returns:
            Message as dictionary or None.
        """
        with Session(self.engine) as session:
            stmt = select(Message).where(Message.uuid == uuid)
            message = session.scalar(stmt)
            return message.to_dict() if message else None

    async def update_message(self, uuid: str, content: str) -> dict:
        """Update message content.

        Args:
            uuid: Message UUID.
            content: New content.

        Returns:
            Updated message as dictionary.
        """
        with Session(self.engine) as session:
            stmt = update(Message).where(Message.uuid == uuid).values(
                content=content,
                updated_at=datetime.utcnow(),
            )
            session.execute(stmt)
            session.commit()

            # Fetch updated message
            stmt = select(Message).where(Message.uuid == uuid)
            message = session.scalar(stmt)
            return message.to_dict() if message else {}

    async def delete_message(self, uuid: str) -> bool:
        """Delete message by UUID.

        Args:
            uuid: Message UUID.

        Returns:
            True if deleted, False otherwise.
        """
        with Session(self.engine) as session:
            stmt = delete(Message).where(Message.uuid == uuid)
            result = session.execute(stmt)
            session.commit()
            return result.rowcount > 0

    async def count_messages(self, conversation_id: str) -> int:
        """Count messages in conversation.

        Args:
            conversation_id: Conversation ID.

        Returns:
            Message count.
        """
        with Session(self.engine) as session:
            stmt = select(func.count()).select_from(Message).where(
                Message.conversation_id == conversation_id
            )
            return session.scalar(stmt) or 0

    def close(self) -> None:
        """Close database connection."""
        self.engine.dispose()
