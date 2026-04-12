"""Phase I: Cloud Build config steps."""
from __future__ import annotations

from typing import Any

from platform_cli.engine.context import ScaffoldContext
from platform_cli.engine.registry import register_step
from platform_cli.engine.step import BaseStep
from platform_cli.templates.renderer import render_to_file


@register_step
class WriteApiBuild(BaseStep):
    step_id = "I.1_write_api_build"
    phase = "I"
    depends_on = ["B.1_create_directories"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        svc = ctx.service("api")
        if not svc:
            return {"skipped": True}

        render_to_file(
            "cloudbuild/api.yaml.j2",
            ctx.project_dir / "cloudbuild" / "api.yaml",
            manifest=ctx.manifest,
            service=svc,
        )

        render_to_file(
            "cloudrun/api.yaml.j2",
            ctx.project_dir / "cloudrun" / "api.yaml",
            manifest=ctx.manifest,
            service=svc,
        )
        return {}


@register_step
class WriteWebBuild(BaseStep):
    step_id = "I.2_write_web_build"
    phase = "I"
    depends_on = ["B.1_create_directories"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        svc = ctx.service("webapp")
        if not svc:
            return {"skipped": True}

        render_to_file(
            "cloudbuild/web.yaml.j2",
            ctx.project_dir / "cloudbuild" / "web.yaml",
            manifest=ctx.manifest,
            service=svc,
        )

        render_to_file(
            "cloudrun/web.yaml.j2",
            ctx.project_dir / "cloudrun" / "web.yaml",
            manifest=ctx.manifest,
            service=svc,
        )
        return {}


@register_step
class WriteTerraformBuild(BaseStep):
    step_id = "I.3_write_terraform_build"
    phase = "I"
    depends_on = ["B.1_create_directories"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        render_to_file(
            "cloudbuild/terraform.yaml.j2",
            ctx.project_dir / "cloudbuild" / "terraform.yaml",
            manifest=ctx.manifest,
        )
        return {}
