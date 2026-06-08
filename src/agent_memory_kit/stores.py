"""Storage backends for agent memories."""

from abc import ABC, abstractmethod

from agent_memory_kit.models import MemoryItem


class MemoryStore(ABC):
    """Interface for storing and retrieving memory items."""

    @abstractmethod
    def add(self, memory: MemoryItem) -> None:
        """Add a memory, replacing an existing item with the same ID."""

    @abstractmethod
    def get(self, id: str) -> MemoryItem | None:
        """Return the memory with the given ID, or ``None`` if it is absent."""

    @abstractmethod
    def list(self) -> list[MemoryItem]:
        """Return all stored memories."""

    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete a memory and return whether it existed."""

    @abstractmethod
    def clear(self) -> None:
        """Delete all stored memories."""


class InMemoryStore(MemoryStore):
    """Store memory items in the current process."""

    def __init__(self) -> None:
        self._memories: dict[str, MemoryItem] = {}

    def add(self, memory: MemoryItem) -> None:
        """Add a memory, replacing an existing item with the same ID."""
        self._memories[memory.id] = memory

    def get(self, id: str) -> MemoryItem | None:
        """Return the memory with the given ID, or ``None`` if it is absent."""
        return self._memories.get(id)

    def list(self) -> list[MemoryItem]:
        """Return all stored memories in insertion order."""
        return list(self._memories.values())

    def delete(self, id: str) -> bool:
        """Delete a memory and return whether it existed."""
        return self._memories.pop(id, None) is not None

    def clear(self) -> None:
        """Delete all stored memories."""
        self._memories.clear()
