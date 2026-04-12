"""platform-cli test [service] — stub, filled in Tier 7."""
from __future__ import annotations

import click
from rich.console import Console

console = Console()


@click.command("test")
@click.argument("service", required=False, default=None)
@click.option(
    "--manifest", "-m",
    type=click.Path(exists=True),
    default=None,
    help="Path to project manifest.",
)
@click.option(
    "--project-dir", "-d",
    type=click.Path(exists=True),
    default=".",
    help="Path to the generated project directory.",
)
def test(service: str | None, manifest: str | None, project_dir: str) -> None:
    """Run tests against a scaffolded project."""
    from pathlib import Path
    from platform_cli.engine.context import ScaffoldContext
    from platform_cli.engine.registry import build_dag
    from platform_cli.engine.runner import StepRunner
    from platform_cli.engine.state import RunState
    from platform_cli.manifest.loader import load_manifest
    from platform_cli.manifest.schema import ProjectManifest, ProjectConfig, CloudConfig
    import platform_cli.steps  # noqa: F401

    pdir = Path(project_dir)
    manifest_path = Path(manifest) if manifest else pdir / "project.manifest.yaml"

    if manifest_path.exists():
        m = load_manifest(manifest_path)
    else:
        m = ProjectManifest(project=ProjectConfig(name=pdir.name, cloud=CloudConfig()))

    ctx = ScaffoldContext(manifest=m, project_dir=pdir)

    # Only run Phase K steps
    all_steps = build_dag()
    test_steps = [s for s in all_steps if s.phase == "K"]

    if service:
        svc_lower = service.lower()
        test_steps = [
            s for s in test_steps
            if svc_lower in s.step_id.lower()
        ]

    if not test_steps:
        console.print("[yellow]No matching test steps found.[/yellow]")
        return

    state = RunState(pdir / ".test-state.json")
    state.clear()

    console.print(f"\n[bold]Running tests ({len(test_steps)} steps)...[/bold]\n")
    runner = StepRunner(test_steps, state)
    runner.run_all(ctx, resume=False)
    console.print("\n[bold green]All tests passed.[/bold green]\n")
