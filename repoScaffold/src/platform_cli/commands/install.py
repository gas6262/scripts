"""platform-cli install [--check-only]"""
from __future__ import annotations

import click
from rich.console import Console

from platform_cli.shell.run import run_cmd
from platform_cli.shell.tools import (
    REQUIRED_TOOLS,
    detect_tool,
    has_brew,
    is_macos,
)

console = Console()


@click.command()
@click.option("--check-only", is_flag=True, help="Only check tools, do not install.")
def install(check_only: bool) -> None:
    """Check / install required CLI tools."""
    console.print("\n[bold]Checking required tools...[/bold]\n")

    missing: list[dict[str, str]] = []
    for tool in REQUIRED_TOOLS:
        found = detect_tool(tool["cmd"])
        status = "[green]found[/green]" if found else "[red]missing[/red]"
        console.print(f"  {status}  {tool['name']}")
        if not found:
            missing.append(tool)

    if not missing:
        console.print("\n[bold green]All tools found.[/bold green]\n")
        return

    if check_only:
        console.print("\n[yellow]Missing tools:[/yellow]")
        for t in missing:
            console.print(f"  - {t['name']}: {t['install_hint']}")
        return

    if is_macos() and has_brew():
        console.print("\n[bold]Installing missing tools via Homebrew...[/bold]\n")
        for t in missing:
            brew_pkg = t.get("brew", "")
            if not brew_pkg:
                console.print(f"  [dim]skip[/dim]    {t['name']} (bundled with another tool)")
                continue
            console.print(f"  [cyan]install[/cyan]  brew install {brew_pkg}")
            result = run_cmd(f"brew install {brew_pkg}", timeout=600)
            if result.ok:
                console.print(f"  [green]done[/green]     {t['name']}")
            else:
                console.print(f"  [red]failed[/red]   {t['name']}: {t['install_hint']}")
        console.print()
    else:
        console.print(
            "\n[yellow]Automated install is currently macOS+Homebrew only. "
            "Install manually:[/yellow]"
        )
        for t in missing:
            console.print(f"  - {t['name']}: {t['install_hint']}")
