"""Phase G: GCP project setup steps."""
from __future__ import annotations

from typing import Any

from platform_cli.engine.context import ScaffoldContext
from platform_cli.engine.registry import register_step
from platform_cli.engine.step import BaseStep
from platform_cli.shell.run import run_cmd


@register_step
class CreateGcpProject(BaseStep):
    step_id = "G.1_create_gcp_project"
    phase = "G"
    depends_on = ["B.1_create_directories"]
    max_retries = 1

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        project_id = ctx.project_id

        # Check if project already exists
        result = run_cmd(f"gcloud projects describe {project_id}")
        if result.ok:
            return {"gcp_project_exists": True, "project_id": project_id}

        # Create the project
        run_cmd(
            f"gcloud projects create {project_id} --name={ctx.project_name}",
            check=True,
        )
        # Set as active project
        run_cmd(f"gcloud config set project {project_id}", check=True)
        return {"gcp_project_created": True, "project_id": project_id}


@register_step
class EnableApis(BaseStep):
    step_id = "G.2_enable_apis"
    phase = "G"
    depends_on = ["G.1_create_gcp_project"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        apis = [
            "run.googleapis.com",
            "cloudbuild.googleapis.com",
            "secretmanager.googleapis.com",
            "artifactregistry.googleapis.com",
        ]
        project_id = ctx.project_id

        for api in apis:
            run_cmd(
                f"gcloud services enable {api} --project={project_id}",
                check=True,
            )
        return {"apis_enabled": apis}


@register_step
class CreateArtifactRegistry(BaseStep):
    step_id = "G.3_create_artifact_registry"
    phase = "G"
    depends_on = ["G.2_enable_apis"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        project_id = ctx.project_id
        region = ctx.region
        repo_name = f"{ctx.project_name.lower().replace(' ', '-')}-docker"

        # Check if registry exists
        result = run_cmd(
            f"gcloud artifacts repositories describe {repo_name} "
            f"--location={region} --project={project_id}"
        )
        if result.ok:
            return {"registry_exists": True, "repo_name": repo_name}

        run_cmd(
            f"gcloud artifacts repositories create {repo_name} "
            f"--repository-format=docker "
            f"--location={region} "
            f"--project={project_id}",
            check=True,
        )
        ctx.set("artifact_registry", repo_name)
        return {"registry_created": True, "repo_name": repo_name}


@register_step
class CreateServiceAccounts(BaseStep):
    step_id = "G.4_create_service_accounts"
    phase = "G"
    depends_on = ["G.1_create_gcp_project"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        project_id = ctx.project_id
        prefix = ctx.project_name.lower().replace(" ", "-")

        accounts = {
            "build": f"{prefix}-build",
            "runtime": f"{prefix}-runtime",
        }

        for role, sa_name in accounts.items():
            email = f"{sa_name}@{project_id}.iam.gserviceaccount.com"
            result = run_cmd(
                f"gcloud iam service-accounts describe {email} "
                f"--project={project_id}"
            )
            if not result.ok:
                run_cmd(
                    f"gcloud iam service-accounts create {sa_name} "
                    f'--display-name="{ctx.project_name} {role} SA" '
                    f"--project={project_id}",
                    check=True,
                )

        ctx.set("service_accounts", accounts)
        return {"service_accounts": accounts}


@register_step
class ConfigureIam(BaseStep):
    step_id = "G.5_configure_iam"
    phase = "G"
    depends_on = ["G.4_create_service_accounts"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        project_id = ctx.project_id
        accounts = ctx.get("service_accounts", {})
        prefix = ctx.project_name.lower().replace(" ", "-")

        build_email = f"{accounts.get('build', prefix + '-build')}@{project_id}.iam.gserviceaccount.com"
        runtime_email = f"{accounts.get('runtime', prefix + '-runtime')}@{project_id}.iam.gserviceaccount.com"

        # Build SA roles
        build_roles = [
            "roles/cloudbuild.builds.builder",
            "roles/artifactregistry.writer",
            "roles/run.admin",
            "roles/secretmanager.secretAccessor",
        ]
        for role in build_roles:
            run_cmd(
                f"gcloud projects add-iam-policy-binding {project_id} "
                f"--member=serviceAccount:{build_email} "
                f"--role={role} --quiet"
            )

        # Runtime SA roles
        runtime_roles = [
            "roles/secretmanager.secretAccessor",
            "roles/logging.logWriter",
            "roles/monitoring.metricWriter",
        ]
        for role in runtime_roles:
            run_cmd(
                f"gcloud projects add-iam-policy-binding {project_id} "
                f"--member=serviceAccount:{runtime_email} "
                f"--role={role} --quiet"
            )

        return {"iam_configured": True}
