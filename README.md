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

## Development

Install the development dependencies and run the checks:

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
```

## License

This project is licensed under the MIT License.
