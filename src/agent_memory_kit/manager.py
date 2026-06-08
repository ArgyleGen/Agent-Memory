"""High-level API for managing agent memories."""

import re
from collections import Counter
from typing import Any
from uuid import uuid4

from agent_memory_kit.models import MemoryItem
from agent_memory_kit.stores import InMemoryStore, MemoryStore


class MemoryManager:
    """Create, recall, and remove memories through a storage backend."""

    def __init__(self, store: MemoryStore | None = None) -> None:
        self._store = store if store is not None else InMemoryStore()

    def remember(
        self,
        content: str,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> MemoryItem:
        """Create and store a memory item."""
        memory = MemoryItem(
            id=str(uuid4()),
            content=content,
            metadata=dict(metadata) if metadata is not None else {},
            tags=list(tags) if tags is not None else [],
        )
        self._store.add(memory)
        return memory

    def recall(
        self,
        query: str | None = None,
        limit: int = 10,
        tags: list[str] | None = None,
    ) -> list[MemoryItem]:
        """Return recent memories filtered by keywords and tags."""
        if limit < 0:
            raise ValueError("limit must be non-negative")

        memories = sorted(
            self._store.list(), key=lambda memory: memory.created_at, reverse=True
        )
        if tags:
            required_tags = set(tags)
            memories = [
                memory for memory in memories if required_tags.issubset(memory.tags)
            ]

        keywords = _tokenize(query) if query is not None else []
        if keywords:
            ranked_memories = [
                (_relevance(memory, keywords), memory) for memory in memories
            ]
            memories = [
                memory
                for relevance, memory in sorted(
                    ranked_memories, key=lambda result: result[0], reverse=True
                )
                if relevance > 0
            ]

        return memories[:limit]

    def forget(self, memory_id: str) -> bool:
        """Remove a memory and return whether it existed."""
        return self._store.delete(memory_id)

    def clear(self) -> None:
        """Remove all memories."""
        self._store.clear()


def _tokenize(text: str) -> list[str]:
    """Return unique, case-insensitive keywords from text."""
    return list(dict.fromkeys(re.findall(r"\w+", text.casefold())))


def _relevance(memory: MemoryItem, keywords: list[str]) -> int:
    """Score a memory by the number of query keyword occurrences."""
    content_words = Counter(re.findall(r"\w+", memory.content.casefold()))
    return sum(content_words[keyword] for keyword in keywords)
