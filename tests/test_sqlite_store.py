import json
import sqlite3
from pathlib import Path

import pytest

from agent_memory_kit import MemoryItem, MemoryStore, SQLiteStore


@pytest.fixture
def database(tmp_path: Path) -> Path:
    return tmp_path / "memories.db"


@pytest.fixture
def store(database: Path) -> SQLiteStore:
    return SQLiteStore(database)


@pytest.fixture
def memory() -> MemoryItem:
    return MemoryItem(
        id="memory-1",
        content="The user prefers concise answers.",
        metadata={"source": "conversation", "priority": 1},
    )


def test_sqlite_store_implements_memory_store(store: SQLiteStore) -> None:
    assert isinstance(store, MemoryStore)


def test_sqlite_store_creates_table_automatically(database: Path) -> None:
    SQLiteStore(database)

    with sqlite3.connect(database) as connection:
        table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'memories'"
        ).fetchone()

    assert table == ("memories",)


def test_sqlite_store_adds_and_gets_memory(
    store: SQLiteStore, memory: MemoryItem
) -> None:
    store.add(memory)

    assert store.get(memory.id) == memory


def test_sqlite_store_replaces_memory_with_same_id(
    store: SQLiteStore, memory: MemoryItem
) -> None:
    replacement = MemoryItem(id=memory.id, content="Updated content")

    store.add(memory)
    store.add(replacement)

    assert store.get(memory.id) == replacement
    assert store.list() == [replacement]


def test_sqlite_store_stores_metadata_as_json(
    database: Path, store: SQLiteStore, memory: MemoryItem
) -> None:
    store.add(memory)

    with sqlite3.connect(database) as connection:
        stored_metadata = connection.execute(
            "SELECT metadata FROM memories WHERE id = ?", (memory.id,)
        ).fetchone()

    assert stored_metadata is not None
    assert json.loads(stored_metadata[0]) == memory.metadata


def test_sqlite_store_get_returns_none_for_unknown_id(store: SQLiteStore) -> None:
    assert store.get("unknown") is None


def test_sqlite_store_lists_memories_in_insertion_order(store: SQLiteStore) -> None:
    first = MemoryItem(id="first", content="First memory")
    second = MemoryItem(id="second", content="Second memory")
    store.add(first)
    store.add(second)

    assert store.list() == [first, second]


def test_sqlite_store_delete_existing_memory(
    store: SQLiteStore, memory: MemoryItem
) -> None:
    store.add(memory)

    assert store.delete(memory.id) is True
    assert store.get(memory.id) is None


def test_sqlite_store_delete_unknown_memory(store: SQLiteStore) -> None:
    assert store.delete("unknown") is False


def test_sqlite_store_clear_removes_all_memories(store: SQLiteStore) -> None:
    store.add(MemoryItem(id="first", content="First memory"))
    store.add(MemoryItem(id="second", content="Second memory"))

    store.clear()

    assert store.list() == []


def test_sqlite_store_supports_in_memory_database() -> None:
    store = SQLiteStore(":memory:")
    memory = MemoryItem(id="memory-1", content="In-memory SQLite")

    store.add(memory)

    assert store.get(memory.id) == memory
