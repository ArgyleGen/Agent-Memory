"""SQLite storage backend for agent memories."""

import json
import sqlite3
from datetime import datetime
from os import PathLike

from agent_memory_kit.models import MemoryItem
from agent_memory_kit.stores import MemoryStore


class SQLiteStore(MemoryStore):
    """Persist memory items in a SQLite database."""

    def __init__(self, database: str | PathLike[str]) -> None:
        self._connection = sqlite3.connect(database)
        self._create_table()

    def _create_table(self) -> None:
        with self._connection as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    tags TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL
                )
                """
            )
            columns = {
                row[1] for row in connection.execute("PRAGMA table_info(memories)")
            }
            if "tags" not in columns:
                connection.execute(
                    "ALTER TABLE memories ADD COLUMN tags TEXT NOT NULL DEFAULT '[]'"
                )

    def add(self, memory: MemoryItem) -> None:
        """Add a memory, replacing an existing item with the same ID."""
        with self._connection as connection:
            connection.execute(
                """
                INSERT INTO memories (id, content, metadata, tags, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    content = excluded.content,
                    metadata = excluded.metadata,
                    tags = excluded.tags,
                    created_at = excluded.created_at
                """,
                (
                    memory.id,
                    memory.content,
                    json.dumps(memory.metadata),
                    json.dumps(memory.tags),
                    memory.created_at.isoformat(),
                ),
            )

    def get(self, id: str) -> MemoryItem | None:
        """Return the memory with the given ID, or ``None`` if it is absent."""
        with self._connection as connection:
            row = connection.execute(
                """
                SELECT id, content, metadata, tags, created_at
                FROM memories
                WHERE id = ?
                """,
                (id,),
            ).fetchone()
        return _memory_from_row(row) if row is not None else None

    def list(self) -> list[MemoryItem]:
        """Return all stored memories in insertion order."""
        with self._connection as connection:
            rows = connection.execute(
                """
                SELECT id, content, metadata, tags, created_at
                FROM memories
                ORDER BY rowid
                """
            ).fetchall()
        return [_memory_from_row(row) for row in rows]

    def delete(self, id: str) -> bool:
        """Delete a memory and return whether it existed."""
        with self._connection as connection:
            cursor = connection.execute("DELETE FROM memories WHERE id = ?", (id,))
        return cursor.rowcount > 0

    def clear(self) -> None:
        """Delete all stored memories."""
        with self._connection as connection:
            connection.execute("DELETE FROM memories")


def _memory_from_row(row: tuple[str, str, str, str, str]) -> MemoryItem:
    """Create a memory item from a SQLite result row."""
    id, content, metadata, tags, created_at = row
    return MemoryItem(
        id=id,
        content=content,
        metadata=json.loads(metadata),
        tags=json.loads(tags),
        created_at=datetime.fromisoformat(created_at),
    )
