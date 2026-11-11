"""Small in-process store for orchestration results."""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class Memory:
    """Store current values and an append-only history of updates."""

    def __init__(self) -> None:
        """Initialize an empty key-value store and history."""
        self._values: Dict[str, Any] = {}
        self._history: List[Dict[str, Any]] = []

    def set(self, key: str, value: Any) -> None:
        """Store a value and record the update in history."""
        try:
            if not key:
                raise ValueError("Memory keys must be non-empty strings")
            self._values[key] = value
            self._history.append({"key": key, "value": value})
            logger.debug("Stored memory value for key %s", key)
        except Exception:
            logger.exception("Unable to store memory value for key %r", key)
            raise

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Return a stored value, or default when the key is absent."""
        try:
            return self._values.get(key, default)
        except Exception:
            logger.exception("Unable to retrieve memory value for key %r", key)
            return default

    def history(self) -> List[Dict[str, Any]]:
        """Return a copy of all successful writes in chronological order."""
        try:
            return list(self._history)
        except Exception:
            logger.exception("Unable to read memory history")
            return []

    def clear(self) -> None:
        """Remove all values and history entries."""
        try:
            self._values.clear()
            self._history.clear()
            logger.info("Memory cleared")
        except Exception:
            logger.exception("Unable to clear memory")
            raise
