"""Phase E: Frontend scaffold steps (React)."""
from __future__ import annotations

from typing import Any

from platform_cli.engine.context import ScaffoldContext
from platform_cli.engine.registry import register_step
from platform_cli.engine.step import BaseStep
from platform_cli.shell.run import run_cmd
from platform_cli.templates.renderer import render_to_file


def _web_enabled(ctx: ScaffoldContext) -> bool:
    return ctx.service("webapp") is not None


@register_step
class InitReact(BaseStep):
    step_id = "E.1_init_react"
    phase = "E"
    depends_on = ["B.1_create_directories"]

    def should_skip(self, ctx: ScaffoldContext) -> bool:
        return super().should_skip(ctx) or not _web_enabled(ctx)

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        web_dir = ctx.project_dir / "services" / "web"
        package_json = web_dir / "package.json"

        if not package_json.exists():
            # Use create-react-app to scaffold
            result = run_cmd(
                f"npx create-react-app {web_dir} --template default",
                timeout=120,
            )
            if not result.ok:
                # Fallback: write minimal package.json
                svc = ctx.service("webapp")
                render_to_file(
                    "services/web/package.json.j2",
                    package_json,
                    project=ctx.manifest.project,
                    service=svc,
                )
        return {"react_initialized": True}


@register_step
class ConfigureProxy(BaseStep):
    step_id = "E.2_configure_proxy"
    phase = "E"
    depends_on = ["E.1_init_react"]

    def should_skip(self, ctx: ScaffoldContext) -> bool:
        return super().should_skip(ctx) or not _web_enabled(ctx)

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        import json

        web_dir = ctx.project_dir / "services" / "web"
        pkg_path = web_dir / "package.json"

        api_svc = ctx.service("api")
        api_port = api_svc.port if api_svc else 3006

        if pkg_path.exists():
            pkg = json.loads(pkg_path.read_text())
            pkg["proxy"] = f"http://localhost:{api_port}"
            pkg_path.write_text(json.dumps(pkg, indent=2) + "\n")
        return {"proxy_configured": True, "api_port": api_port}


@register_step
class WriteItemsFetch(BaseStep):
    step_id = "E.3_write_items_fetch"
    phase = "E"
    depends_on = ["E.2_configure_proxy"]

    def should_skip(self, ctx: ScaffoldContext) -> bool:
        return super().should_skip(ctx) or not _web_enabled(ctx)

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        web_src = ctx.project_dir / "services" / "web" / "src"
        web_src.mkdir(parents=True, exist_ok=True)

        api_svc = ctx.service("api")
        api_port = api_svc.port if api_svc else 3006

        render_to_file(
            "services/web/App.js.j2",
            web_src / "App.js",
            api_port=api_port,
        )
        render_to_file(
            "services/web/api.js.j2",
            web_src / "api.js",
            api_port=api_port,
        )
        return {"items_fetch_written": True}


@register_step
class WriteFrontendDockerfile(BaseStep):
    step_id = "E.4_write_frontend_dockerfile"
    phase = "E"
    depends_on = ["E.1_init_react"]

    def should_skip(self, ctx: ScaffoldContext) -> bool:
        return super().should_skip(ctx) or not _web_enabled(ctx)

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        api_svc = ctx.service("api")
        api_name = api_svc.name if api_svc else "api"

        render_to_file(
            "services/web/Dockerfile.j2",
            ctx.project_dir / "services" / "web" / "Dockerfile",
            api_name=api_name,
        )
        return {}
