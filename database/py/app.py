"""Example database application with message persistence."""

import asyncio
import uuid as uuid_module
from .database_service import DatabaseService


async def main():
    """Run example database operations."""

    # Initialize database
    db = DatabaseService(db_path="sqlite:///./messages.db")

    print("\n" + "=" * 60)
    print("Database Message Service Example")
    print("=" * 60 + "\n")

    try:
        # Create conversation ID
        conversation_id = str(uuid_module.uuid4())
        print(f"Conversation ID: {conversation_id}\n")

        # Insert messages
        print("Inserting messages...")
        messages_data = [
            {
                "content": "Hello, how are you?",
                "role": "user",
                "name": "Alice",
            },
            {
                "content": "I'm doing well, thanks for asking!",
                "role": "assistant",
                "name": "Bot",
            },
            {
                "content": "Tell me about your capabilities.",
                "role": "user",
                "name": "Alice",
            },
        ]

        message_ids = []
        for msg_data in messages_data:
            msg_uuid = str(uuid_module.uuid4())
            result = await db.insert_message(
                uuid=msg_uuid,
                conversation_id=conversation_id,
                **msg_data,
            )
            message_ids.append(msg_uuid)
            print(f"  Created: {result['content'][:40]}...")

        print(f"\nTotal messages in conversation: {await db.count_messages(conversation_id)}\n")

        # Retrieve messages
        print("Retrieving conversation messages...")
        messages = await db.get_messages_by_conversation_id(conversation_id)
        for msg in messages:
            print(f"  {msg['role']:10} ({msg['name']:8}): {msg['content'][:40]}...")

        # Update message
        if message_ids:
            print(f"\nUpdating first message...")
            updated = await db.update_message(
                uuid=message_ids[0],
                content="Hello, how are you doing today?",
            )
            print(f"  Updated: {updated['content']}")

        # Get single message
        if message_ids:
            print(f"\nFetching single message...")
            msg = await db.get_message_by_uuid(message_ids[0])
            if msg:
                print(f"  {msg['role']:10}: {msg['content']}")

        # Delete message
        if len(message_ids) > 2:
            print(f"\nDeleting last message...")
            deleted = await db.delete_message(message_ids[2])
            print(f"  Deleted: {deleted}")
            print(
                f"  Remaining messages: {await db.count_messages(conversation_id)}"
            )

    except Exception as error:
        print(f"Error: {error}")

    finally:
        db.close()

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
