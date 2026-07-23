"""Click CLI group: scaffold, install, test."""
from __future__ import annotations

import click

from platform_cli.commands.scaffold import scaffold
from platform_cli.commands.install import install
from platform_cli.commands.test_cmd import test
from platform_cli.commands.create_agent_identity import create_agent_identity


@click.group()
@click.version_option(version="0.1.0", prog_name="platform-cli")
def cli() -> None:
    """Scaffold, provision, test, and deploy full-stack apps on GCP."""


cli.add_command(scaffold)
cli.add_command(install)
cli.add_command(test)
cli.add_command(create_agent_identity)
