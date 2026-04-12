"""RunState: JSON persistence for resumability."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class RunState:
    """Tracks which steps have completed and their outputs.

    State is persisted as JSON so a failed run can resume where it left off.
    """

    def __init__(self, state_file: Path) -> None:
        self._path = state_file
        self._data: dict[str, Any] = {"completed": {}, "failed": None}
        if self._path.exists():
            self._data = json.loads(self._path.read_text())

    def is_completed(self, step_id: str) -> bool:
        return step_id in self._data["completed"]

    def mark_completed(self, step_id: str, outputs: dict[str, Any]) -> None:
        self._data["completed"][step_id] = outputs
        self._save()

    def mark_failed(self, step_id: str, error: str) -> None:
        self._data["failed"] = {"step_id": step_id, "error": error}
        self._save()

    def outputs(self, step_id: str) -> dict[str, Any]:
        return self._data["completed"].get(step_id, {})

    def clear(self) -> None:
        self._data = {"completed": {}, "failed": None}
        if self._path.exists():
            self._path.unlink()

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2))
