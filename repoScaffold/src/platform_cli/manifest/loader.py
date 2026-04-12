"""Load YAML manifest, validate with Pydantic, and apply defaults."""
from __future__ import annotations

from pathlib import Path

import yaml

from platform_cli.manifest.defaults import DEFAULT_PORTS, DEFAULT_STACKS
from platform_cli.manifest.schema import ProjectManifest


def load_manifest(path: Path) -> ProjectManifest:
    """Read a YAML manifest, apply defaults, return a validated model."""
    raw = yaml.safe_load(path.read_text())
    manifest = ProjectManifest.model_validate(raw)
    _apply_defaults(manifest)
    return manifest


def _apply_defaults(m: ProjectManifest) -> None:
    name_lower = m.project.name.lower().replace(" ", "-")

    if not m.project.cloud.project_id:
        m.project.cloud.project_id = name_lower

    if not m.database.db_name:
        m.database.db_name = name_lower.replace("-", "_")

    for svc in m.services:
        if not svc.name:
            svc.name = svc.type
        if not svc.subdomain:
            svc.subdomain = svc.name
        if svc.port == 0:
            svc.port = DEFAULT_PORTS.get(svc.type, 8080)
        if not svc.stack:
            svc.stack = DEFAULT_STACKS.get(svc.type, "")
