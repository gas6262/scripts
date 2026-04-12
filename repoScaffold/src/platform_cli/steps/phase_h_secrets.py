"""Phase H: Secret management steps."""
from __future__ import annotations

from typing import Any

import yaml

from platform_cli.engine.context import ScaffoldContext
from platform_cli.engine.registry import register_step
from platform_cli.engine.step import BaseStep
from platform_cli.shell.run import run_cmd
from platform_cli.templates.renderer import render_to_file


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

        # Read API .env for secret values
        env_file = ctx.project_dir / "services" / "api" / ".env"
        env_vars: dict[str, str] = {}
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    env_vars[key.strip()] = val.strip()

        synced = []
        for key, value in env_vars.items():
            secret_name = key.lower().replace("_", "-")

            # Check if secret exists
            result = run_cmd(
                f"gcloud secrets describe {secret_name} --project={project_id}"
            )
            if not result.ok:
                run_cmd(
                    f"gcloud secrets create {secret_name} --project={project_id} "
                    f"--replication-policy=automatic",
                    check=True,
                )

            # Add version with value
            run_cmd(
                f'printf "%s" "{value}" | gcloud secrets versions add {secret_name} '
                f"--data-file=- --project={project_id}",
                check=True,
            )
            synced.append(key)

        return {"synced_secrets": synced}


@register_step
class WriteEnvExampleSecrets(BaseStep):
    step_id = "H.3_write_env_example_secrets"
    phase = "H"
    depends_on = ["H.1_write_secret_manifest"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        # Append secret-backed vars to .env.example
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
