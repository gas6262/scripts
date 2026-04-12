"""platform-cli install [--check-only] — stub, filled in Tier 7."""
from __future__ import annotations

import click


@click.command()
@click.option("--check-only", is_flag=True, help="Only check tools, do not install.")
def install(check_only: bool) -> None:
    """Check / install required CLI tools."""
    # Implemented in Tier 7
    from platform_cli.shell.tools import REQUIRED_TOOLS, detect_tool
    from rich.console import Console

    console = Console()
    console.print("\n[bold]Checking required tools...[/bold]\n")
    all_ok = True
    for tool in REQUIRED_TOOLS:
        found = detect_tool(tool["cmd"])
        status = "[green]found[/green]" if found else "[red]missing[/red]"
        console.print(f"  {status}  {tool['name']}")
        if not found:
            all_ok = False
            console.print(f"         Install: {tool['install_hint']}")

    if all_ok:
        console.print("\n[bold green]All tools found.[/bold green]\n")
    else:
        console.print("\n[yellow]Some tools are missing. Install them and re-run.[/yellow]\n")
        if not check_only:
            console.print("[dim]Pass --check-only to skip installation prompts.[/dim]")
