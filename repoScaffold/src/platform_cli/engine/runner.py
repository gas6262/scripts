"""StepRunner: execute steps with retry + state persistence."""
from __future__ import annotations

import time
from typing import Any

from rich.console import Console
from rich.panel import Panel

from platform_cli.engine.context import ScaffoldContext
from platform_cli.engine.state import RunState
from platform_cli.engine.step import BaseStep

console = Console()


class StepRunner:
    """Execute an ordered list of steps, persisting progress."""

    def __init__(self, steps: list[BaseStep], state: RunState) -> None:
        self.steps = steps
        self.state = state

    def run_all(self, ctx: ScaffoldContext, *, resume: bool = True) -> None:
        if not resume:
            self.state.clear()

        for step in self.steps:
            if resume and self.state.is_completed(step.step_id):
                console.print(f"  [dim]skip (done)[/dim]  {step.step_id}")
                continue

            if step.should_skip(ctx):
                console.print(f"  [yellow]skip (phase)[/yellow]  {step.step_id}")
                continue

            if ctx.dry_run:
                console.print(f"  [cyan]dry-run[/cyan]     {step.step_id}")
                continue

            self._execute(step, ctx)

    def _execute(self, step: BaseStep, ctx: ScaffoldContext) -> dict[str, Any]:
        attempts = step.max_retries + 1
        last_err: Exception | None = None

        for attempt in range(1, attempts + 1):
            try:
                console.print(f"  [green]run[/green]         {step.step_id}", end="")
                if attempts > 1:
                    console.print(f" [dim](attempt {attempt}/{attempts})[/dim]", end="")
                console.print()

                outputs = step.run(ctx) or {}
                self.state.mark_completed(step.step_id, outputs)
                return outputs
            except Exception as exc:
                last_err = exc
                if attempt < attempts:
                    console.print(f"  [yellow]retry[/yellow]       {step.step_id}: {exc}")
                    time.sleep(1)

        assert last_err is not None
        self.state.mark_failed(step.step_id, str(last_err))
        console.print(
            Panel(
                f"[red bold]Step failed:[/red bold] {step.step_id}\n{last_err}",
                title="Error",
                border_style="red",
            )
        )
        raise last_err
