"""High-level API for managing agent memories."""

from typing import Any
from uuid import uuid4

from agent_memory_kit.models import MemoryItem
from agent_memory_kit.stores import InMemoryStore, MemoryStore


class MemoryManager:
    """Create, recall, and remove memories through a storage backend."""

    def __init__(self, store: MemoryStore | None = None) -> None:
        self._store = store if store is not None else InMemoryStore()

    def remember(
        self, content: str, metadata: dict[str, Any] | None = None
    ) -> MemoryItem:
        """Create and store a memory item."""
        memory = MemoryItem(
            id=str(uuid4()),
            content=content,
            metadata=dict(metadata) if metadata is not None else {},
        )
        self._store.add(memory)
        return memory

    def recall(self, query: str | None = None, limit: int = 10) -> list[MemoryItem]:
        """Return recent memories, optionally filtered by content."""
        if limit < 0:
            raise ValueError("limit must be non-negative")

        memories = sorted(
            self._store.list(), key=lambda memory: memory.created_at, reverse=True
        )
        if query is not None:
            normalized_query = query.casefold()
            memories = [
                memory
                for memory in memories
                if normalized_query in memory.content.casefold()
            ]

        return memories[:limit]

    def forget(self, memory_id: str) -> bool:
        """Remove a memory and return whether it existed."""
        return self._store.delete(memory_id)

    def clear(self) -> None:
        """Remove all memories."""
        self._store.clear()
