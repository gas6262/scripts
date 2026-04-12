"""BaseStep ABC: the contract every scaffold step implements."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from platform_cli.engine.context import ScaffoldContext


class BaseStep(ABC):
    """Abstract base for every scaffold step.

    Subclasses must set the class-level attributes and implement ``run()``.
    """

    step_id: str = ""
    phase: str = ""
    depends_on: list[str] = []
    max_retries: int = 0

    @abstractmethod
    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        """Execute the step, returning a dict of outputs."""

    def inputs(self) -> list[str]:
        """Descriptive list of what this step needs (for documentation)."""
        return []

    def outputs_spec(self) -> list[str]:
        """Descriptive list of what this step produces."""
        return []

    def should_skip(self, ctx: ScaffoldContext) -> bool:
        """Return True if this step should be skipped given the context."""
        return self.phase in ctx.skip_phases

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.step_id}>"
