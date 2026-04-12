"""ScaffoldContext: shared state bag passed to every step."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from platform_cli.manifest.schema import ProjectManifest


@dataclass
class ScaffoldContext:
    """Mutable state bag shared across all steps during a scaffold run."""

    manifest: ProjectManifest
    project_dir: Path
    dry_run: bool = False
    skip_phases: list[str] = field(default_factory=list)
    extras: dict[str, Any] = field(default_factory=dict)

    @property
    def project_name(self) -> str:
        return self.manifest.project.name

    @property
    def project_id(self) -> str:
        return self.manifest.project.cloud.project_id

    @property
    def region(self) -> str:
        return self.manifest.project.cloud.region

    def service(self, svc_type: str):
        """Return the first enabled service matching *svc_type*, or None."""
        for s in self.manifest.services:
            if s.type == svc_type and s.enabled:
                return s
        return None

    def set(self, key: str, value: Any) -> None:
        self.extras[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.extras.get(key, default)
