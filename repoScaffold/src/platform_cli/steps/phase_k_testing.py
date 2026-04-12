"""Phase K: Testing steps."""
from __future__ import annotations

import os
import signal
import subprocess
import time
from typing import Any

from rich.console import Console

from platform_cli.engine.context import ScaffoldContext
from platform_cli.engine.registry import register_step
from platform_cli.engine.step import BaseStep
from platform_cli.shell.run import run_cmd

console = Console()


def _ensure_deps(dir_path: str) -> None:
    if not os.path.isdir(os.path.join(dir_path, "node_modules")):
        run_cmd("npm install", cwd=dir_path, check=True, timeout=300)


@register_step
class ApiLint(BaseStep):
    step_id = "K.1_api_lint"
    phase = "K"
    depends_on = ["D.3_write_api_source"]

    def should_skip(self, ctx: ScaffoldContext) -> bool:
        return super().should_skip(ctx) or ctx.service("api") is None

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        api_dir = str(ctx.project_dir / "services" / "api")
        _ensure_deps(api_dir)
        result = run_cmd("npm run lint", cwd=api_dir)
        if not result.ok:
            raise RuntimeError(f"Lint failed:\n{result.stdout}\n{result.stderr}")
        return {"lint_passed": True}


@register_step
class ApiHealth(BaseStep):
    step_id = "K.2_api_health"
    phase = "K"
    depends_on = ["D.3_write_api_source"]
    max_retries = 0

    def should_skip(self, ctx: ScaffoldContext) -> bool:
        return super().should_skip(ctx) or ctx.service("api") is None

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        svc = ctx.service("api")
        port = svc.port if svc else 3006
        api_dir = str(ctx.project_dir / "services" / "api")
        _ensure_deps(api_dir)

        # Spawn the API in its own process group so we can kill the whole tree.
        proc = subprocess.Popen(
            ["node", "src/index.js"],
            cwd=api_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            preexec_fn=os.setsid,
        )

        health_ok = False
        last_err = ""
        try:
            deadline = time.time() + 20
            url = f"http://localhost:{port}/health"
            while time.time() < deadline:
                r = run_cmd(f"curl -sf {url}", timeout=5)
                if r.ok:
                    health_ok = True
                    break
                last_err = r.stderr or r.stdout
                time.sleep(0.5)
        finally:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)

        if not health_ok:
            logs = ""
            if proc.stdout:
                logs = proc.stdout.read() or ""
            raise RuntimeError(
                f"API /health did not respond on :{port}\nlast curl: {last_err}\nprocess log:\n{logs[-1000:]}"
            )
        return {"health_ok": True, "port": port}


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
            timeout=600,
        )
        return {"image_tag": tag, "build_ok": result.ok}


@register_step
class FrontendSmoke(BaseStep):
    step_id = "K.4_frontend_smoke"
    phase = "K"
    depends_on = ["E.3_write_items_fetch"]

    def should_skip(self, ctx: ScaffoldContext) -> bool:
        return super().should_skip(ctx) or ctx.service("webapp") is None

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        web_dir = str(ctx.project_dir / "services" / "web")
        _ensure_deps(web_dir)
        result = run_cmd("npm run build", cwd=web_dir, timeout=300)
        if not result.ok:
            raise RuntimeError(
                f"Frontend build failed:\n{result.stdout}\n{result.stderr}"
            )
        return {"build_ok": True}


@register_step
class TerraformValidate(BaseStep):
    step_id = "K.5_terraform_validate"
    phase = "K"
    depends_on = ["J.6_write_dev_env"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        tf_dir = str(ctx.project_dir / "infra" / "terraform" / "envs" / "dev")
        run_cmd("terraform init -backend=false", cwd=tf_dir, check=True, timeout=180)
        result = run_cmd("terraform validate", cwd=tf_dir)
        if not result.ok:
            raise RuntimeError(
                f"terraform validate failed:\n{result.stdout}\n{result.stderr}"
            )
        return {"validate_ok": True}


@register_step
class TerraformPlan(BaseStep):
    """Plan requires GCP credentials; soft-fail with a clear warning."""

    step_id = "K.6_terraform_plan"
    phase = "K"
    depends_on = ["K.5_terraform_validate"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        tf_dir = str(ctx.project_dir / "infra" / "terraform" / "envs" / "dev")
        result = run_cmd("terraform plan -input=false", cwd=tf_dir, timeout=180)
        if not result.ok:
            console.print(
                "[yellow]terraform plan did not succeed — usually needs GCP auth "
                "and the project to exist. Run `gcloud auth application-default login`.[/yellow]"
            )
        return {"plan_ok": result.ok}
