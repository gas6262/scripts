"""Phase H: Secret management steps."""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import yaml

from platform_cli.engine.context import ScaffoldContext
from platform_cli.engine.registry import register_step
from platform_cli.engine.step import BaseStep
from platform_cli.shell.run import run_cmd


def _read_env(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        out[key.strip()] = val.strip()
    return out


@register_step
class WriteSecretManifest(BaseStep):
    step_id = "H.1_write_secret_manifest"
    phase = "H"
    depends_on = ["B.1_create_directories"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        secrets = [
            {"name": "MONGODB_URI", "source": "services/api/.env"},
            {"name": "DB_NAME", "source": "services/api/.env"},
        ]

        manifest_path = ctx.project_dir / "secrets.manifest.yaml"
        manifest_path.write_text(
            yaml.dump(
                {"secrets": secrets},
                default_flow_style=False,
                sort_keys=False,
            )
        )
        return {"secret_manifest_path": str(manifest_path)}


@register_step
class SyncSecretsToGcp(BaseStep):
    step_id = "H.2_sync_secrets_to_gcp"
    phase = "H"
    depends_on = ["H.1_write_secret_manifest", "G.2_enable_apis"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        project_id = ctx.project_id
        env_vars = _read_env(ctx.project_dir / "services" / "api" / ".env")

        synced: list[str] = []
        for key, value in env_vars.items():
            secret_name = key.lower().replace("_", "-")

            exists = run_cmd(
                f"gcloud secrets describe {secret_name} --project={project_id}"
            ).ok
            if not exists:
                run_cmd(
                    f"gcloud secrets create {secret_name} "
                    f"--project={project_id} --replication-policy=automatic",
                    check=True,
                )

            # Write value to a temp file to avoid shell-escaping pitfalls.
            with tempfile.NamedTemporaryFile(
                "w", delete=False, prefix="secret-", suffix=".txt"
            ) as tmp:
                tmp.write(value)
                tmp_path = tmp.name
            try:
                run_cmd(
                    f"gcloud secrets versions add {secret_name} "
                    f"--data-file={tmp_path} --project={project_id}",
                    check=True,
                )
            finally:
                Path(tmp_path).unlink(missing_ok=True)

            synced.append(key)

        return {"synced_secrets": synced}


@register_step
class WriteEnvExampleSecrets(BaseStep):
    step_id = "H.3_write_env_example_secrets"
    phase = "H"
    depends_on = ["H.1_write_secret_manifest"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        env_example = ctx.project_dir / ".env.example"
        if env_example.exists():
            content = env_example.read_text()
            if "# Secrets (managed by GCP Secret Manager)" not in content:
                content += (
                    "\n# Secrets (managed by GCP Secret Manager)\n"
                    "# MONGODB_URI=<from Secret Manager>\n"
                    "# DB_NAME=<from Secret Manager>\n"
                )
                env_example.write_text(content)
        return {}
