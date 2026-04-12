"""DAG builder + Kahn's topological sort."""
from __future__ import annotations

from collections import defaultdict, deque

from platform_cli.engine.step import BaseStep


class CycleError(Exception):
    """Raised when the step DAG contains a cycle."""


def topological_sort(steps: list[BaseStep]) -> list[BaseStep]:
    """Return steps in dependency-respecting order using Kahn's algorithm."""
    step_map: dict[str, BaseStep] = {s.step_id: s for s in steps}

    # Build adjacency and in-degree
    in_degree: dict[str, int] = defaultdict(int)
    dependents: dict[str, list[str]] = defaultdict(list)

    for s in steps:
        in_degree.setdefault(s.step_id, 0)
        for dep in s.depends_on:
            dependents[dep].append(s.step_id)
            in_degree[s.step_id] += 1

    queue: deque[str] = deque(
        sid for sid, deg in in_degree.items() if deg == 0
    )
    ordered: list[str] = []

    while queue:
        sid = queue.popleft()
        ordered.append(sid)
        for child in dependents[sid]:
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue.append(child)

    if len(ordered) != len(steps):
        remaining = set(s.step_id for s in steps) - set(ordered)
        raise CycleError(f"Cycle detected involving steps: {remaining}")

    return [step_map[sid] for sid in ordered]
