import pytest

from agent_memory_kit import InMemoryStore, MemoryItem, MemoryStore


@pytest.fixture
def store() -> InMemoryStore:
    return InMemoryStore()


@pytest.fixture
def memory() -> MemoryItem:
    return MemoryItem(id="memory-1", content="The user prefers concise answers.")


def test_in_memory_store_implements_memory_store() -> None:
    assert isinstance(InMemoryStore(), MemoryStore)


def test_add_and_get_memory(store: InMemoryStore, memory: MemoryItem) -> None:
    store.add(memory)

    assert store.get(memory.id) == memory


def test_add_replaces_memory_with_same_id(
    store: InMemoryStore, memory: MemoryItem
) -> None:
    replacement = MemoryItem(id=memory.id, content="Updated content")

    store.add(memory)
    store.add(replacement)

    assert store.get(memory.id) == replacement
    assert store.list() == [replacement]


def test_get_returns_none_for_unknown_id(store: InMemoryStore) -> None:
    assert store.get("unknown") is None


def test_list_returns_all_memories_in_insertion_order(store: InMemoryStore) -> None:
    first = MemoryItem(id="first", content="First memory")
    second = MemoryItem(id="second", content="Second memory")

    store.add(first)
    store.add(second)

    assert store.list() == [first, second]


def test_list_returns_a_new_list(store: InMemoryStore, memory: MemoryItem) -> None:
    store.add(memory)

    memories = store.list()
    memories.clear()

    assert store.list() == [memory]


def test_delete_existing_memory(store: InMemoryStore, memory: MemoryItem) -> None:
    store.add(memory)

    assert store.delete(memory.id) is True
    assert store.get(memory.id) is None


def test_delete_unknown_memory(store: InMemoryStore) -> None:
    assert store.delete("unknown") is False


def test_clear_removes_all_memories(store: InMemoryStore) -> None:
    store.add(MemoryItem(id="first", content="First memory"))
    store.add(MemoryItem(id="second", content="Second memory"))

    store.clear()

    assert store.list() == []


def test_in_memory_store_preserves_tags(store: InMemoryStore) -> None:
    memory = MemoryItem(id="tagged", content="Tagged memory", tags=["project"])

    store.add(memory)

    assert store.get(memory.id) == memory
    assert store.list() == [memory]
