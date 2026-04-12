"""platform-cli test [service] — run Phase K tests against a scaffolded project."""
from __future__ import annotations

import sys
from pathlib import Path

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
@click.option(
    "--skip", "-s",
    multiple=True,
    help="Substring(s) matching step_ids to skip (e.g. docker, terraform).",
)
@click.option(
    "--only", "-o",
    multiple=True,
    help="Substring(s) matching step_ids to include (overrides service filter).",
)
def test(
    service: str | None,
    manifest: str | None,
    project_dir: str,
    skip: tuple[str, ...],
    only: tuple[str, ...],
) -> None:
    """Run tests against a scaffolded project.

    Without arguments, runs all Phase K tests. Pass a service name (api, web,
    worker) to run only its tests, or use --only/--skip for finer control.
    """
    from platform_cli.engine.context import ScaffoldContext
    from platform_cli.engine.registry import build_dag
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

    all_steps = build_dag()
    test_steps = [s for s in all_steps if s.phase == "K"]

    if only:
        needles = [o.lower() for o in only]
        test_steps = [s for s in test_steps if any(n in s.step_id.lower() for n in needles)]
    elif service:
        svc_lower = service.lower()
        test_steps = [s for s in test_steps if svc_lower in s.step_id.lower()]

    if skip:
        needles = [s.lower() for s in skip]
        test_steps = [s for s in test_steps if not any(n in s.step_id.lower() for n in needles)]

    if not test_steps:
        console.print("[yellow]No matching test steps found.[/yellow]")
        return

    state = RunState(pdir / ".test-state.json")
    state.clear()

    console.print(f"\n[bold]Running tests ({len(test_steps)} steps)...[/bold]\n")

    passed: list[str] = []
    failed: list[tuple[str, str]] = []
    skipped: list[str] = []

    for step in test_steps:
        if step.should_skip(ctx):
            console.print(f"  [yellow]skip[/yellow]    {step.step_id}")
            skipped.append(step.step_id)
            continue
        try:
            console.print(f"  [green]run[/green]     {step.step_id}")
            step.run(ctx)
            console.print(f"  [green]pass[/green]    {step.step_id}")
            passed.append(step.step_id)
        except Exception as exc:  # noqa: BLE001
            msg = str(exc).splitlines()[0][:200] if str(exc) else exc.__class__.__name__
            console.print(f"  [red]fail[/red]    {step.step_id}: {msg}")
            failed.append((step.step_id, str(exc)))

    console.print("")
    console.print(f"[bold]Summary:[/bold] {len(passed)} passed, {len(failed)} failed, {len(skipped)} skipped")
    for sid, err in failed:
        console.print(f"  [red]FAIL[/red] {sid}")
        for line in err.splitlines()[:6]:
            console.print(f"    {line}")

    if failed:
        sys.exit(1)
    console.print("\n[bold green]All tests passed.[/bold green]\n")
