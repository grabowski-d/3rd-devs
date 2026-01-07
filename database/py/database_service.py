"""Database Service - Python implementation of database/DatabaseService.ts"""
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime


class DatabaseService:
    def __init__(self, db_path: str = 'database/database.db'):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Create messages table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT NOT NULL,
                conversation_id TEXT NOT NULL,
                content TEXT NOT NULL,
                name TEXT,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def insert_message(self, message: Dict[str, Any]) -> Any:
        """
        Insert a message into the database.
        
        Args:
            message: Dict with keys:
                - uuid: str
                - conversation_id: str
                - content: str
                - name: Optional[str]
                - role: str (e.g., 'user' or 'assistant')
                
        Returns:
            Cursor result from execute
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages (uuid, conversation_id, content, name, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''', (
            message['uuid'],
            message['conversation_id'],
            message['content'],
            message.get('name'),
            message['role']
        ))
        
        conn.commit()
        result = cursor.lastrowid
        conn.close()
        
        return result
    
    async def get_messages_by_conversation_id(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all messages for a specific conversation.
        
        Args:
            conversation_id: The ID of the conversation
            
        Returns:
            List of message dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM messages WHERE conversation_id = ?', (conversation_id,))
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(row) for row in rows]
    
    async def get_message_by_uuid(self, uuid: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a message by its UUID.
        
        Args:
            uuid: The UUID of the message
            
        Returns:
            Message dictionary or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM messages WHERE uuid = ?', (uuid,))
        row = cursor.fetchone()
        
        conn.close()
        
        return dict(row) if row else None
    
    async def update_message(self, uuid: str, content: str) -> Any:
        """
        Update a message's content.
        
        Args:
            uuid: The UUID of the message to update
            content: The new content
            
        Returns:
            Cursor result from execute
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE messages 
            SET content = ?, updated_at = CURRENT_TIMESTAMP
            WHERE uuid = ?
        ''', (content, uuid))
        
        conn.commit()
        result = cursor.rowcount
        conn.close()
        
        return result
    
    async def delete_message(self, uuid: str) -> Any:
        """
        Delete a message by its UUID.
        
        Args:
            uuid: The UUID of the message to delete
            
        Returns:
            Number of rows deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM messages WHERE uuid = ?', (uuid,))
        
        conn.commit()
        result = cursor.rowcount
        conn.close()
        
        return result
