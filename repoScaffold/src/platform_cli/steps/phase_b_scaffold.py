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
            "agents",
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


@register_step
class WriteAgentLoop(BaseStep):
    step_id = "B.10_write_agent_loop"
    phase = "B"
    depends_on = ["B.1_create_directories"]

    # Built-in agent templates shipped with the scaffolder
    BUILTIN_AGENTS = ["developer", "reviewer", "ops"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        import os
        from pathlib import Path

        # Determine which agents to scaffold
        manifest_roles = {r.name: r for r in ctx.manifest.agents.roles}
        agent_names = list(manifest_roles.keys()) if manifest_roles else self.BUILTIN_AGENTS

        agents_dir = ctx.project_dir / "agents"
        scaffolded = []

        for name in agent_names:
            agent_dir = agents_dir / name
            agent_dir.mkdir(parents=True, exist_ok=True)

            role = manifest_roles.get(name)
            agent_ctx = {
                "sleep_seconds": role.sleep_seconds if role else None,
                "max_turns": role.max_turns if role else None,
            }

            template_dir = Path(f"agents/{name}")
            prompt_template = f"agents/{name}/PROMPT.md.j2"
            config_template = f"agents/{name}/config.yaml.j2"

            try:
                render_to_file(
                    prompt_template,
                    agent_dir / "PROMPT.md",
                    manifest=ctx.manifest,
                    agent=agent_ctx,
                )
            except Exception:
                # No built-in template — create a placeholder
                (agent_dir / "PROMPT.md").write_text(
                    f"# {name.title()} Agent\n\n"
                    f"You are the **{name}** agent for **{ctx.manifest.project.name}**.\n\n"
                    f"Define this agent's behavior by editing this file.\n"
                )

            try:
                render_to_file(
                    config_template,
                    agent_dir / "config.yaml",
                    manifest=ctx.manifest,
                    agent=agent_ctx,
                )
            except Exception:
                defaults = {"developer": (600, 1000), "reviewer": (1800, 200), "ops": (1800, 100)}
                sleep_s, max_t = defaults.get(name, (600, 500))
                (agent_dir / "config.yaml").write_text(
                    f"name: {name}\n"
                    f"description: {name.title()} agent\n"
                    f"sleep_seconds: {agent_ctx.get('sleep_seconds') or sleep_s}\n"
                    f"max_turns: {agent_ctx.get('max_turns') or max_t}\n"
                )

            scaffolded.append(name)

        # Write shared loop.sh and setup-vm.sh
        render_to_file(
            "project/loop.sh.j2",
            ctx.project_dir / "loop.sh",
            manifest=ctx.manifest,
        )
        render_to_file(
            "project/setup-vm.sh.j2",
            ctx.project_dir / "setup-vm.sh",
            manifest=ctx.manifest,
        )

        os.chmod(ctx.project_dir / "loop.sh", 0o755)
        os.chmod(ctx.project_dir / "setup-vm.sh", 0o755)

        return {"agents": scaffolded}
