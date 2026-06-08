from datetime import datetime, timedelta, timezone

import pytest

from agent_memory_kit import InMemoryStore, MemoryItem, MemoryManager


@pytest.fixture
def manager() -> MemoryManager:
    return MemoryManager()


def test_remember_stores_and_returns_memory(manager: MemoryManager) -> None:
    metadata = {"source": "conversation"}

    memory = manager.remember("The user prefers concise answers.", metadata)

    assert memory.id
    assert memory.content == "The user prefers concise answers."
    assert memory.metadata == metadata
    assert manager.recall() == [memory]


def test_remember_copies_metadata(manager: MemoryManager) -> None:
    metadata = {"source": "conversation"}

    memory = manager.remember("A memory", metadata)
    metadata["source"] = "changed"

    assert memory.metadata == {"source": "conversation"}


def test_recall_returns_latest_memories_with_limit() -> None:
    store = InMemoryStore()
    manager = MemoryManager(store)
    now = datetime.now(timezone.utc)
    oldest = MemoryItem(id="oldest", content="Oldest", created_at=now)
    middle = MemoryItem(
        id="middle", content="Middle", created_at=now + timedelta(seconds=1)
    )
    newest = MemoryItem(
        id="newest", content="Newest", created_at=now + timedelta(seconds=2)
    )
    for memory in (middle, oldest, newest):
        store.add(memory)

    assert manager.recall(limit=2) == [newest, middle]


def test_recall_filters_content_case_insensitively() -> None:
    store = InMemoryStore()
    manager = MemoryManager(store)
    matching = MemoryItem(id="matching", content="The user likes Python")
    other = MemoryItem(id="other", content="The user likes Rust")
    store.add(matching)
    store.add(other)

    assert manager.recall(query="PYTHON") == [matching]


def test_recall_rejects_negative_limit(manager: MemoryManager) -> None:
    with pytest.raises(ValueError, match="limit must be non-negative"):
        manager.recall(limit=-1)


def test_forget_removes_memory(manager: MemoryManager) -> None:
    memory = manager.remember("A memory")

    assert manager.forget(memory.id) is True
    assert manager.recall() == []


def test_forget_returns_false_for_unknown_memory(manager: MemoryManager) -> None:
    assert manager.forget("unknown") is False


def test_clear_removes_all_memories(manager: MemoryManager) -> None:
    manager.remember("First memory")
    manager.remember("Second memory")

    manager.clear()

    assert manager.recall() == []
