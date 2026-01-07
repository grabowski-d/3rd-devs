"""Database service for SQLite with ORM."""
import sqlite3
from typing import List, Dict, Optional, Any
from datetime import datetime
import json


class DatabaseService:
    """SQLite database service for message persistence."""

    def __init__(self, db_path: str = 'database/database.db'):
        """Initialize database service.
        
        Args:
            db_path: Path to SQLite database file.
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Initialize database and create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid TEXT NOT NULL UNIQUE,
                    conversation_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    name TEXT,
                    role TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_conversation_id 
                ON messages(conversation_id)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_uuid 
                ON messages(uuid)
            ''')
            conn.commit()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection

    async def insert_message(self, message: Dict[str, Any]) -> int:
        """Insert a message into the database.
        
        Args:
            message: Dict with keys: uuid, conversation_id, content, role, name (optional)
        
        Returns:
            Row ID of inserted message.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO messages (
                    uuid, conversation_id, content, name, role, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                message['uuid'],
                message['conversation_id'],
                message['content'],
                message.get('name'),
                message['role'],
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat()
            ))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            raise ValueError(f'Failed to insert message: {e}')

    async def get_messages_by_conversation_id(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a conversation.
        
        Args:
            conversation_id: Conversation ID to fetch messages for.
        
        Returns:
            List of message dicts.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM messages 
            WHERE conversation_id = ? 
            ORDER BY created_at ASC
        ''', (conversation_id,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    async def get_message_by_uuid(self, uuid: str) -> Optional[Dict[str, Any]]:
        """Get a single message by UUID.
        
        Args:
            uuid: Message UUID.
        
        Returns:
            Message dict or None if not found.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM messages WHERE uuid = ?', (uuid,))
        row = cursor.fetchone()
        
        return dict(row) if row else None

    async def update_message(self, uuid: str, content: str) -> bool:
        """Update message content.
        
        Args:
            uuid: Message UUID.
            content: New message content.
        
        Returns:
            True if message was updated, False otherwise.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE messages 
            SET content = ?, updated_at = ? 
            WHERE uuid = ?
        ''', (content, datetime.utcnow().isoformat(), uuid))
        
        conn.commit()
        return cursor.rowcount > 0

    async def delete_message(self, uuid: str) -> bool:
        """Delete a message by UUID.
        
        Args:
            uuid: Message UUID.
        
        Returns:
            True if message was deleted, False otherwise.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM messages WHERE uuid = ?', (uuid,))
        conn.commit()
        
        return cursor.rowcount > 0

    async def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Get summary stats for a conversation.
        
        Args:
            conversation_id: Conversation ID.
        
        Returns:
            Dict with message counts and timestamps.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_messages,
                SUM(CASE WHEN role = 'user' THEN 1 ELSE 0 END) as user_messages,
                SUM(CASE WHEN role = 'assistant' THEN 1 ELSE 0 END) as assistant_messages,
                MIN(created_at) as first_message,
                MAX(created_at) as last_message
            FROM messages
            WHERE conversation_id = ?
        ''', (conversation_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else {}

    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def __del__(self):
        """Ensure connection is closed on cleanup."""
        self.close()
