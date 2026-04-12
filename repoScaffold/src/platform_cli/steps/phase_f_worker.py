"""Phase F: Worker scaffold steps."""
from __future__ import annotations

from typing import Any

from platform_cli.engine.context import ScaffoldContext
from platform_cli.engine.registry import register_step
from platform_cli.engine.step import BaseStep
from platform_cli.templates.renderer import render_to_file


def _worker_enabled(ctx: ScaffoldContext) -> bool:
    return ctx.service("worker") is not None


@register_step
class ScaffoldWorker(BaseStep):
    step_id = "F.1_scaffold_worker"
    phase = "F"
    depends_on = ["B.1_create_directories"]

    def should_skip(self, ctx: ScaffoldContext) -> bool:
        return super().should_skip(ctx) or not _worker_enabled(ctx)

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        worker_dir = ctx.project_dir / "services" / "worker"
        worker_dir.mkdir(parents=True, exist_ok=True)

        svc = ctx.service("worker")

        render_to_file(
            "services/worker/main.py.j2",
            worker_dir / "main.py",
            service=svc,
        )
        render_to_file(
            "services/worker/requirements.txt.j2",
            worker_dir / "requirements.txt",
            service=svc,
        )
        return {"worker_scaffolded": True}


@register_step
class WriteWorkerDockerfile(BaseStep):
    step_id = "F.2_write_worker_dockerfile"
    phase = "F"
    depends_on = ["F.1_scaffold_worker"]

    def should_skip(self, ctx: ScaffoldContext) -> bool:
        return super().should_skip(ctx) or not _worker_enabled(ctx)

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        svc = ctx.service("worker")

        render_to_file(
            "services/worker/Dockerfile.j2",
            ctx.project_dir / "services" / "worker" / "Dockerfile",
            service=svc,
        )
        return {}


@register_step
class WriteWorkerEnv(BaseStep):
    step_id = "F.3_write_worker_env"
    phase = "F"
    depends_on = ["F.1_scaffold_worker"]

    def should_skip(self, ctx: ScaffoldContext) -> bool:
        return super().should_skip(ctx) or not _worker_enabled(ctx)

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        env_file = ctx.project_dir / "services" / "worker" / ".env"
        if not env_file.exists():
            env_file.write_text("PORT=80\n")
        return {}
