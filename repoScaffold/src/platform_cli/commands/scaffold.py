"""platform-cli scaffold <name> [--manifest] [--skip-phase] [--dry-run]"""
from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console

from platform_cli.engine.context import ScaffoldContext
from platform_cli.engine.registry import build_dag
from platform_cli.engine.runner import StepRunner
from platform_cli.engine.state import RunState
from platform_cli.manifest.loader import load_manifest
from platform_cli.manifest.schema import ProjectManifest, ProjectConfig, CloudConfig

# Trigger step registration by importing the steps package
import platform_cli.steps  # noqa: F401

console = Console()


@click.command()
@click.argument("name")
@click.option(
    "--manifest", "-m",
    type=click.Path(exists=True, path_type=Path),
    help="Path to a YAML manifest file.",
)
@click.option(
    "--skip-phase", "-s",
    multiple=True,
    help="Phase letter(s) to skip (e.g. C, G, H).",
)
@click.option("--dry-run", is_flag=True, help="Show execution plan without running.")
@click.option("--no-resume", is_flag=True, help="Ignore previous run state.")
@click.option(
    "--output-dir", "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Parent directory for the generated project (default: cwd).",
)
def scaffold(
    name: str,
    manifest: Path | None,
    skip_phase: tuple[str, ...],
    dry_run: bool,
    no_resume: bool,
    output_dir: Path | None,
) -> None:
    """Scaffold a new full-stack project."""
    if manifest:
        m = load_manifest(manifest)
        # Override project name from CLI arg
        m.project.name = name
    else:
        m = ProjectManifest(
            project=ProjectConfig(name=name, cloud=CloudConfig()),
        )

    parent = output_dir or Path.cwd()
    project_dir = parent / name
    project_dir.mkdir(parents=True, exist_ok=True)

    ctx = ScaffoldContext(
        manifest=m,
        project_dir=project_dir,
        dry_run=dry_run,
        skip_phases=[p.upper() for p in skip_phase],
    )

    state_file = project_dir / ".scaffold-state.json"
    state = RunState(state_file)

    console.print(f"\n[bold]Scaffolding project:[/bold] {name}")
    console.print(f"  Directory: {project_dir}")
    console.print(f"  Skip phases: {list(ctx.skip_phases) or 'none'}")
    console.print(f"  Dry run: {dry_run}\n")

    steps = build_dag()
    runner = StepRunner(steps, state)
    runner.run_all(ctx, resume=not no_resume)

    console.print("\n[bold green]Done.[/bold green]\n")
