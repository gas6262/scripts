"""Phase D: API scaffold steps (Express + Mongoose)."""
from __future__ import annotations

from typing import Any

from platform_cli.engine.context import ScaffoldContext
from platform_cli.engine.registry import register_step
from platform_cli.engine.step import BaseStep
from platform_cli.shell.run import run_cmd
from platform_cli.templates.renderer import render_to_file


def _api_enabled(ctx: ScaffoldContext) -> bool:
    return ctx.service("api") is not None


@register_step
class InitExpress(BaseStep):
    step_id = "D.1_init_express"
    phase = "D"
    depends_on = ["B.1_create_directories"]

    def should_skip(self, ctx: ScaffoldContext) -> bool:
        return super().should_skip(ctx) or not _api_enabled(ctx)

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        api_dir = ctx.project_dir / "services" / "api"
        api_dir.mkdir(parents=True, exist_ok=True)

        svc = ctx.service("api")
        render_to_file(
            "services/api/package.json.j2",
            api_dir / "package.json",
            project=ctx.manifest.project,
            service=svc,
        )
        return {"api_package_json": True}


@register_step
class AddMongoose(BaseStep):
    step_id = "D.2_add_mongoose"
    phase = "D"
    depends_on = ["D.1_init_express"]

    def should_skip(self, ctx: ScaffoldContext) -> bool:
        return super().should_skip(ctx) or not _api_enabled(ctx)

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        # Mongoose is included in the package.json template
        return {"mongoose_configured": True}


@register_step
class WriteApiSource(BaseStep):
    step_id = "D.3_write_api_source"
    phase = "D"
    depends_on = ["D.2_add_mongoose"]

    def should_skip(self, ctx: ScaffoldContext) -> bool:
        return super().should_skip(ctx) or not _api_enabled(ctx)

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        api_src = ctx.project_dir / "services" / "api" / "src"
        api_src.mkdir(parents=True, exist_ok=True)

        svc = ctx.service("api")
        db = ctx.manifest.database

        render_to_file(
            "services/api/index.js.j2",
            api_src / "index.js",
            service=svc,
            database=db,
        )
        render_to_file(
            "services/api/db.js.j2",
            api_src / "db.js",
            database=db,
        )
        render_to_file(
            "services/api/models.js.j2",
            api_src / "models.js",
            database=db,
        )
        render_to_file(
            "services/api/.eslintrc.json.j2",
            ctx.project_dir / "services" / "api" / ".eslintrc.json",
        )
        return {"api_source_written": True}


@register_step
class WriteApiDockerfile(BaseStep):
    step_id = "D.4_write_api_dockerfile"
    phase = "D"
    depends_on = ["D.1_init_express"]

    def should_skip(self, ctx: ScaffoldContext) -> bool:
        return super().should_skip(ctx) or not _api_enabled(ctx)

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        render_to_file(
            "services/api/Dockerfile.j2",
            ctx.project_dir / "services" / "api" / "Dockerfile",
        )
        return {}


@register_step
class WriteApiEnv(BaseStep):
    step_id = "D.5_write_api_env"
    phase = "D"
    depends_on = ["D.1_init_express"]

    def should_skip(self, ctx: ScaffoldContext) -> bool:
        return super().should_skip(ctx) or not _api_enabled(ctx)

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        env_file = ctx.project_dir / "services" / "api" / ".env"
        if not env_file.exists():
            db = ctx.manifest.database
            env_file.write_text(
                f"MONGODB_URI=mongodb+srv://<user>:<password>@{db.atlas_cluster.lower()}.xxxxx.mongodb.net/{db.db_name}?retryWrites=true&w=majority\n"
                f"DB_NAME={db.db_name}\n"
                f"PORT=80\n"
            )
        return {}
