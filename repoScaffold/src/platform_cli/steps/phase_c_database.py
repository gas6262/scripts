"""Phase C: Database setup (MongoDB Atlas).

Idempotent flow:
  C.1 atlas_auth            — ensure logged in
  C.2 ensure_cluster        — verify cluster exists
  C.3 ensure_db_user        — create DB user + strong password (if not existing)
  C.4 get_connection_string — resolve the SRV URI and bake user credentials in
  C.5 seed_items            — create `items` collection and upsert a sample doc
  C.6 write_api_env         — write MONGODB_URI + DB_NAME to services/api/.env
"""
from __future__ import annotations

import json
import secrets
import shlex
import string
from typing import Any
from urllib.parse import quote_plus

from rich.console import Console

from platform_cli.engine.context import ScaffoldContext
from platform_cli.engine.registry import register_step
from platform_cli.engine.step import BaseStep
from platform_cli.shell.run import run_cmd

console = Console()


def _gen_password(n: int = 24) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))


@register_step
class AtlasAuth(BaseStep):
    step_id = "C.1_atlas_auth"
    phase = "C"
    depends_on = ["B.1_create_directories"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        if run_cmd("atlas auth whoami").ok:
            return {"atlas_authenticated": True}
        raise RuntimeError(
            "Not logged in to Atlas. Run `atlas auth login` "
            "(or `atlas config init` with an API key) and re-run."
        )


@register_step
class EnsureCluster(BaseStep):
    step_id = "C.2_ensure_cluster"
    phase = "C"
    depends_on = ["C.1_atlas_auth"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        cluster = ctx.manifest.database.atlas_cluster
        result = run_cmd(f"atlas clusters describe {cluster} -o json")
        if not result.ok:
            raise RuntimeError(
                f"Atlas cluster '{cluster}' not found in the current project. "
                f"Either create it in the Atlas UI, or update "
                f"`database.atlas_cluster` in the manifest.\n{result.stderr}"
            )
        data = json.loads(result.stdout)
        ctx.set("atlas_cluster_data", data)
        return {"cluster": cluster, "state": data.get("stateName")}


@register_step
class EnsureDbUser(BaseStep):
    step_id = "C.3_ensure_db_user"
    phase = "C"
    depends_on = ["C.2_ensure_cluster"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        username = (ctx.project_name.lower().replace(" ", "-") + "-app")[:64]
        existing = run_cmd(f"atlas dbusers describe {username} -o json")
        if existing.ok:
            # User exists — rotate password so we can bake it into the URI.
            password = _gen_password()
            run_cmd(
                f"atlas dbusers update {username} --password {shlex.quote(password)}",
                check=True,
            )
        else:
            password = _gen_password()
            run_cmd(
                f"atlas dbusers create atlasAdmin "
                f"--username {username} "
                f"--password {shlex.quote(password)}",
                check=True,
            )
        ctx.set("db_username", username)
        ctx.set("db_password", password)
        return {"username": username}


@register_step
class GetConnectionString(BaseStep):
    step_id = "C.4_get_connection_string"
    phase = "C"
    depends_on = ["C.3_ensure_db_user"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        cluster = ctx.manifest.database.atlas_cluster
        db_name = ctx.manifest.database.db_name

        r = run_cmd(f"atlas clusters connectionStrings describe {cluster} -o json")
        if not r.ok:
            raise RuntimeError(f"Failed to get Atlas connection string: {r.stderr}")
        data = json.loads(r.stdout)
        srv = data.get("standardSrv") or data.get("standard")
        if not srv:
            raise RuntimeError(f"No connection string found: {data}")

        user = quote_plus(ctx.get("db_username", ""))
        pw = quote_plus(ctx.get("db_password", ""))
        host = srv.split("://", 1)[1]
        uri = f"mongodb+srv://{user}:{pw}@{host}/{db_name}?retryWrites=true&w=majority"
        ctx.set("mongodb_uri", uri)
        return {"has_uri": True}


@register_step
class SeedItems(BaseStep):
    step_id = "C.5_seed_items"
    phase = "C"
    depends_on = ["C.4_get_connection_string"]
    max_retries = 2

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        uri = ctx.get("mongodb_uri")
        db_name = ctx.manifest.database.db_name
        script = (
            "db.items.updateOne("
            '{"name":"example item"},'
            '{"$setOnInsert":{"name":"example item"}},'
            "{upsert:true});"
            'print("ok");'
        )
        cmd = f"mongosh {shlex.quote(uri)} --quiet --eval {shlex.quote(script)}"
        r = run_cmd(cmd, timeout=60)
        if not r.ok or "ok" not in r.stdout:
            raise RuntimeError(f"Seed failed: {r.stderr or r.stdout}")
        return {"seeded": True, "db": db_name}


@register_step
class WriteApiEnv(BaseStep):
    step_id = "C.6_write_api_env"
    phase = "C"
    depends_on = ["C.4_get_connection_string"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        uri = ctx.get("mongodb_uri")
        db_name = ctx.manifest.database.db_name
        env_file = ctx.project_dir / "services" / "api" / ".env"
        env_file.parent.mkdir(parents=True, exist_ok=True)
        env_file.write_text(
            f"MONGODB_URI={uri}\n"
            f"DB_NAME={db_name}\n"
        )
        return {"env_written": str(env_file)}
