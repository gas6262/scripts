"""Phase B: Repository / folder scaffold steps."""
from __future__ import annotations

from typing import Any

import yaml

from platform_cli.engine.context import ScaffoldContext
from platform_cli.engine.registry import register_step
from platform_cli.engine.step import BaseStep
from platform_cli.templates.renderer import render_to_file


@register_step
class CreateDirectories(BaseStep):
    step_id = "B.1_create_directories"
    phase = "B"
    depends_on = ["A.2_install_tools"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        dirs = [
            "cli",
            "services/api/src",
            "services/web",
            "services/worker",
            "infra/terraform/modules",
            "infra/terraform/envs/dev",
            "cloudbuild",
            "cloudrun",
            ".vscode",
            ".claude",
        ]
        for d in dirs:
            (ctx.project_dir / d).mkdir(parents=True, exist_ok=True)
        return {"directories_created": len(dirs)}


@register_step
class WriteManifest(BaseStep):
    step_id = "B.2_write_manifest"
    phase = "B"
    depends_on = ["B.1_create_directories"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        dest = ctx.project_dir / "project.manifest.yaml"
        data = ctx.manifest.model_dump()
        dest.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
        return {"manifest_path": str(dest)}


@register_step
class WriteGitignore(BaseStep):
    step_id = "B.3_write_gitignore"
    phase = "B"
    depends_on = ["B.1_create_directories"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        render_to_file(
            "project/.gitignore.j2",
            ctx.project_dir / ".gitignore",
            project=ctx.manifest.project,
        )
        return {}


@register_step
class WriteDockerCompose(BaseStep):
    step_id = "B.4_write_docker_compose"
    phase = "B"
    depends_on = ["B.1_create_directories"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        render_to_file(
            "project/docker-compose.yml.j2",
            ctx.project_dir / "docker-compose.yml",
            manifest=ctx.manifest,
            services=ctx.manifest.services,
        )
        return {}


@register_step
class WriteAgentsMd(BaseStep):
    step_id = "B.5_write_agents_md"
    phase = "B"
    depends_on = ["B.1_create_directories"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        render_to_file(
            "project/AGENTS.md.j2",
            ctx.project_dir / "AGENTS.md",
            manifest=ctx.manifest,
        )
        return {}


@register_step
class WriteVSCode(BaseStep):
    step_id = "B.6_write_vscode"
    phase = "B"
    depends_on = ["B.1_create_directories"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        render_to_file(
            "vscode/launch.json.j2",
            ctx.project_dir / ".vscode" / "launch.json",
            manifest=ctx.manifest,
        )
        render_to_file(
            "vscode/tasks.json.j2",
            ctx.project_dir / ".vscode" / "tasks.json",
            manifest=ctx.manifest,
        )
        return {}


@register_step
class WriteClaude(BaseStep):
    step_id = "B.7_write_claude"
    phase = "B"
    depends_on = ["B.1_create_directories"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        render_to_file(
            "claude/settings.json.j2",
            ctx.project_dir / ".claude" / "settings.json",
            manifest=ctx.manifest,
        )
        return {}


@register_step
class WriteReadme(BaseStep):
    step_id = "B.8_write_readme"
    phase = "B"
    depends_on = ["B.1_create_directories"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        render_to_file(
            "project/README.md.j2",
            ctx.project_dir / "README.md",
            manifest=ctx.manifest,
        )
        return {}


@register_step
class WriteEnvExample(BaseStep):
    step_id = "B.9_write_env_example"
    phase = "B"
    depends_on = ["B.1_create_directories"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        render_to_file(
            "project/.env.example.j2",
            ctx.project_dir / ".env.example",
            manifest=ctx.manifest,
        )
        return {}
