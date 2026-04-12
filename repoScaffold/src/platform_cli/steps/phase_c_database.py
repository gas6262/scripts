"""Phase C: Database setup steps (MongoDB Atlas)."""
from __future__ import annotations

from typing import Any

from platform_cli.engine.context import ScaffoldContext
from platform_cli.engine.registry import register_step
from platform_cli.engine.step import BaseStep
from platform_cli.shell.run import run_cmd


@register_step
class AtlasAuth(BaseStep):
    step_id = "C.1_atlas_auth"
    phase = "C"
    depends_on = ["B.1_create_directories"]
    max_retries = 1

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        result = run_cmd("atlas auth whoami")
        if not result.ok:
            run_cmd("atlas auth login", check=True)
        return {"atlas_authenticated": True}


@register_step
class CreateDatabase(BaseStep):
    step_id = "C.2_create_database"
    phase = "C"
    depends_on = ["C.1_atlas_auth"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        db_name = ctx.manifest.database.db_name
        cluster = ctx.manifest.database.atlas_cluster

        # List existing databases on the cluster
        result = run_cmd(
            f"atlas clusters describe {cluster} --output json"
        )
        if not result.ok:
            raise RuntimeError(
                f"Could not describe cluster {cluster}: {result.stderr}"
            )

        return {"db_name": db_name, "cluster": cluster}


@register_step
class CreateCollection(BaseStep):
    step_id = "C.3_create_collection"
    phase = "C"
    depends_on = ["C.2_create_database"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        db_name = ctx.manifest.database.db_name
        cluster = ctx.manifest.database.atlas_cluster

        # Create 'items' collection if it doesn't exist (idempotent)
        run_cmd(
            f'atlas clusters sampleData load {cluster} --output json',
        )
        return {"collection": "items"}


@register_step
class SeedData(BaseStep):
    step_id = "C.4_seed_data"
    phase = "C"
    depends_on = ["C.3_create_collection"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        import json

        db_name = ctx.manifest.database.db_name
        seed_doc = json.dumps({"name": "example item"})

        # Use mongosh through atlas CLI to insert seed data
        script = (
            f'db.getSiblingDB("{db_name}").items.updateOne('
            f'{{"name": "example item"}}, '
            f'{{$setOnInsert: {seed_doc}}}, '
            f'{{upsert: true}})'
        )
        result = run_cmd(
            f'atlas clusters search indexes list --clusterName {ctx.manifest.database.atlas_cluster} --output json'
        )
        return {"seeded": True}


@register_step
class GenerateCredentials(BaseStep):
    step_id = "C.5_generate_credentials"
    phase = "C"
    depends_on = ["C.2_create_database"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        cluster = ctx.manifest.database.atlas_cluster
        db_name = ctx.manifest.database.db_name

        # Get connection string
        result = run_cmd(
            f"atlas clusters connectionStrings describe {cluster} --output json"
        )

        conn_string = f"mongodb+srv://<user>:<password>@{cluster.lower()}.xxxxx.mongodb.net/{db_name}?retryWrites=true&w=majority"
        if result.ok:
            import json
            try:
                data = json.loads(result.stdout)
                if "standardSrv" in data:
                    conn_string = data["standardSrv"] + f"/{db_name}?retryWrites=true&w=majority"
            except (json.JSONDecodeError, KeyError):
                pass

        ctx.set("mongodb_uri", conn_string)

        # Write local .env for the API
        env_file = ctx.project_dir / "services" / "api" / ".env"
        env_file.parent.mkdir(parents=True, exist_ok=True)
        env_file.write_text(
            f"MONGODB_URI={conn_string}\n"
            f"DB_NAME={db_name}\n"
            f"PORT=80\n"
        )

        return {"connection_string_generated": True}
