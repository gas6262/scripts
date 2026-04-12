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

        if package_json.exists():
            return {"react_initialized": True, "source": "existing"}

        # Vite is non-interactive when --template is provided.
        result = run_cmd(
            f"npm create vite@latest {web_dir.name} -- --template react",
            cwd=str(web_dir.parent),
            timeout=120,
        )
        if result.ok and package_json.exists():
            return {"react_initialized": True, "source": "vite"}

        # Fallback: render our template set directly.
        svc = ctx.service("webapp")
        api_svc = ctx.service("api")
        api_port = api_svc.port if api_svc else 3006
        web_port = svc.port if svc else 3005
        for tmpl, rel in [
            ("services/web/package.json.j2", "package.json"),
            ("services/web/vite.config.js.j2", "vite.config.js"),
            ("services/web/index.html.j2", "index.html"),
            ("services/web/main.jsx.j2", "src/main.jsx"),
        ]:
            render_to_file(
                tmpl,
                web_dir / rel,
                project=ctx.manifest.project,
                service=svc,
                api_port=api_port,
                web_port=web_port,
            )
        return {"react_initialized": True, "source": "fallback"}


@register_step
class ConfigureProxy(BaseStep):
    step_id = "E.2_configure_proxy"
    phase = "E"
    depends_on = ["E.1_init_react"]

    def should_skip(self, ctx: ScaffoldContext) -> bool:
        return super().should_skip(ctx) or not _web_enabled(ctx)

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        web_dir = ctx.project_dir / "services" / "web"

        svc = ctx.service("webapp")
        api_svc = ctx.service("api")
        api_port = api_svc.port if api_svc else 3006
        web_port = svc.port if svc else 3005

        render_to_file(
            "services/web/vite.config.js.j2",
            web_dir / "vite.config.js",
            api_port=api_port,
            web_port=web_port,
        )
        return {"proxy_configured": True, "api_port": api_port, "web_port": web_port}


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
            "services/web/App.jsx.j2",
            web_src / "App.jsx",
            api_port=api_port,
        )
        render_to_file(
            "services/web/api.js.j2",
            web_src / "api.js",
            api_port=api_port,
        )
        render_to_file(
            "services/web/index.html.j2",
            ctx.project_dir / "services" / "web" / "index.html",
            project=ctx.manifest.project,
        )
        # Drop the CRA-era App.js if Vite didn't overwrite it (Vite's default is App.jsx).
        legacy_app = web_src / "App.js"
        if legacy_app.exists():
            legacy_app.unlink()
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
        web_dir = ctx.project_dir / "services" / "web"

        render_to_file(
            "services/web/Dockerfile.j2",
            web_dir / "Dockerfile",
            api_name=api_name,
        )
        render_to_file(
            "services/web/.dockerignore.j2",
            web_dir / ".dockerignore",
        )
        return {}
