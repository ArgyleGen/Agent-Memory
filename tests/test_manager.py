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


def test_keyword_search_finds_single_word_case_insensitively() -> None:
    manager = MemoryManager()
    matching = manager.remember("The user enjoys Python")
    manager.remember("The user enjoys Rust")

    assert manager.recall(query="PYTHON") == [matching]


def test_keyword_search_supports_multiple_words_and_sorts_by_relevance() -> None:
    manager = MemoryManager()
    one_match = manager.remember("Python is useful")
    two_matches = manager.remember("Python agents use memory")
    three_matches = manager.remember("Python memory improves agent memory")

    assert manager.recall(query="python memory") == [
        three_matches,
        two_matches,
        one_match,
    ]


def test_keyword_search_returns_no_results_without_matches() -> None:
    manager = MemoryManager()
    manager.remember("The user enjoys Python")

    assert manager.recall(query="rust") == []


def test_keyword_search_respects_limit() -> None:
    manager = MemoryManager()
    manager.remember("Python")
    manager.remember("Python Python")
    most_relevant = manager.remember("Python Python Python")

    assert manager.recall(query="python", limit=1) == [most_relevant]


def test_remember_stores_and_copies_tags(manager: MemoryManager) -> None:
    tags = ["user", "preference"]

    memory = manager.remember("The user prefers concise answers.", tags=tags)
    tags.append("changed")

    assert memory.tags == ["user", "preference"]


def test_recall_filters_by_single_tag(manager: MemoryManager) -> None:
    project = manager.remember("Project deadline", tags=["project"])
    manager.remember("User preference", tags=["user", "preference"])

    assert manager.recall(tags=["project"]) == [project]


def test_recall_filters_by_all_requested_tags(manager: MemoryManager) -> None:
    matching = manager.remember("User preference", tags=["user", "preference"])
    manager.remember("User profile", tags=["user"])
    manager.remember("General preference", tags=["preference"])

    assert manager.recall(tags=["user", "preference"]) == [matching]


def test_recall_combines_keyword_and_tag_filters(manager: MemoryManager) -> None:
    matching = manager.remember("Python project", tags=["project"])
    manager.remember("Rust project", tags=["project"])
    manager.remember("Python preference", tags=["preference"])

    assert manager.recall(query="python", tags=["project"]) == [matching]
