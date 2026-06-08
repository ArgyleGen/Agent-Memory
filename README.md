# agent-memory-kit

`agent-memory-kit` is an open-source Python library for building memory systems for
AI agents.

## Installation

```bash
pip install agent-memory-kit
```

## Usage

```python
from agent_memory_kit import MemoryManager

memory = MemoryManager()
saved = memory.remember(
    "The user prefers concise answers.",
    metadata={"source": "conversation"},
)

recent_memories = memory.recall()
matching_memories = memory.recall(query="concise", limit=5)
memory.forget(saved.id)
memory.clear()
```

To persist memories in SQLite, pass a `SQLiteStore` to the manager:

```python
from agent_memory_kit import MemoryManager, SQLiteStore

memory = MemoryManager(store=SQLiteStore("agent-memory.db"))
memory.remember("This memory persists between processes.")
from agent_memory_kit import InMemoryStore, MemoryItem

store = InMemoryStore()
from agent_memory_kit import MemoryItem

memory = MemoryItem(
    id="memory-1",
    content="The user prefers concise answers.",
    metadata={"source": "conversation"},
)

store.add(memory)
stored_memory = store.get("memory-1")
all_memories = store.list()
store.delete("memory-1")
store.clear()
```

## Development

Install the development dependencies and run the checks:

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
```

## License

This project is licensed under the MIT License.
