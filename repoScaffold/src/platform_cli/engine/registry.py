"""@register_step decorator + build_dag() helper."""
from __future__ import annotations

from platform_cli.engine.dag import topological_sort
from platform_cli.engine.step import BaseStep

_REGISTRY: list[type[BaseStep]] = []


def register_step(cls: type[BaseStep]) -> type[BaseStep]:
    """Class decorator that registers a step for DAG construction."""
    _REGISTRY.append(cls)
    return cls


def build_dag() -> list[BaseStep]:
    """Instantiate all registered steps and return them in topological order."""
    steps = [cls() for cls in _REGISTRY]
    return topological_sort(steps)


def registered_steps() -> list[type[BaseStep]]:
    """Return the raw list of registered step classes."""
    return list(_REGISTRY)
