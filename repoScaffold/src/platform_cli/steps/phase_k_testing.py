"""Phase K: Testing steps."""
from __future__ import annotations

from typing import Any

from platform_cli.engine.context import ScaffoldContext
from platform_cli.engine.registry import register_step
from platform_cli.engine.step import BaseStep
from platform_cli.shell.run import run_cmd


@register_step
class ApiLint(BaseStep):
    step_id = "K.1_api_lint"
    phase = "K"
    depends_on = ["D.3_write_api_source"]

    def should_skip(self, ctx: ScaffoldContext) -> bool:
        return super().should_skip(ctx) or ctx.service("api") is None

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        api_dir = str(ctx.project_dir / "services" / "api")

        # Install deps first if needed
        if not (ctx.project_dir / "services" / "api" / "node_modules").exists():
            run_cmd("npm install", cwd=api_dir, check=True)

        result = run_cmd("npm run lint", cwd=api_dir)
        return {"lint_passed": result.ok, "output": result.stdout}


@register_step
class ApiHealth(BaseStep):
    step_id = "K.2_api_health"
    phase = "K"
    depends_on = ["D.3_write_api_source"]
    max_retries = 2

    def should_skip(self, ctx: ScaffoldContext) -> bool:
        return super().should_skip(ctx) or ctx.service("api") is None

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        svc = ctx.service("api")
        port = svc.port if svc else 3006

        result = run_cmd(
            f"curl -sf http://localhost:{port}/health",
            timeout=10,
        )
        if not result.ok:
            from rich.console import Console
            Console().print(
                "[yellow]API health check failed — is the API running?[/yellow]"
            )
        return {"health_ok": result.ok}


@register_step
class ApiDockerBuild(BaseStep):
    step_id = "K.3_api_docker_build"
    phase = "K"
    depends_on = ["D.4_write_api_dockerfile"]

    def should_skip(self, ctx: ScaffoldContext) -> bool:
        return super().should_skip(ctx) or ctx.service("api") is None

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        api_dir = str(ctx.project_dir / "services" / "api")
        tag = f"{ctx.project_name.lower().replace(' ', '-')}-api:test"

        result = run_cmd(
            f"docker build -t {tag} .",
            cwd=api_dir,
            check=True,
            timeout=120,
        )
        return {"docker_build_ok": result.ok, "image_tag": tag}


@register_step
class FrontendSmoke(BaseStep):
    step_id = "K.4_frontend_smoke"
    phase = "K"
    depends_on = ["E.3_write_items_fetch"]

    def should_skip(self, ctx: ScaffoldContext) -> bool:
        return super().should_skip(ctx) or ctx.service("webapp") is None

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        web_dir = str(ctx.project_dir / "services" / "web")

        # Check that build succeeds
        if not (ctx.project_dir / "services" / "web" / "node_modules").exists():
            run_cmd("npm install", cwd=web_dir, check=True, timeout=120)

        result = run_cmd("npm run build", cwd=web_dir, timeout=120)
        return {"build_ok": result.ok}


@register_step
class TerraformValidate(BaseStep):
    step_id = "K.5_terraform_validate"
    phase = "K"
    depends_on = ["J.6_write_dev_env"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        tf_dir = str(ctx.project_dir / "infra" / "terraform" / "envs" / "dev")

        run_cmd("terraform init -backend=false", cwd=tf_dir, check=True)
        result = run_cmd("terraform validate", cwd=tf_dir)
        return {"validate_ok": result.ok, "output": result.stdout}


@register_step
class TerraformPlan(BaseStep):
    step_id = "K.6_terraform_plan"
    phase = "K"
    depends_on = ["K.5_terraform_validate"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        tf_dir = str(ctx.project_dir / "infra" / "terraform" / "envs" / "dev")

        result = run_cmd("terraform plan -input=false", cwd=tf_dir, timeout=120)
        return {"plan_ok": result.ok}
