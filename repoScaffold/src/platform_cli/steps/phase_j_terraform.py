"""Phase J: Terraform generation steps."""
from __future__ import annotations

from typing import Any

from platform_cli.engine.context import ScaffoldContext
from platform_cli.engine.registry import register_step
from platform_cli.engine.step import BaseStep
from platform_cli.templates.renderer import render_to_file


@register_step
class WriteProviderTf(BaseStep):
    step_id = "J.1_write_provider_tf"
    phase = "J"
    depends_on = ["B.1_create_directories"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        render_to_file(
            "infra/terraform/main.tf.j2",
            ctx.project_dir / "infra" / "terraform" / "main.tf",
            manifest=ctx.manifest,
        )
        render_to_file(
            "infra/terraform/variables.tf.j2",
            ctx.project_dir / "infra" / "terraform" / "variables.tf",
            manifest=ctx.manifest,
        )
        render_to_file(
            "infra/terraform/outputs.tf.j2",
            ctx.project_dir / "infra" / "terraform" / "outputs.tf",
            manifest=ctx.manifest,
        )
        return {}


@register_step
class WriteCloudRunModule(BaseStep):
    step_id = "J.2_write_cloudrun_module"
    phase = "J"
    depends_on = ["J.1_write_provider_tf"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        mod_dir = "infra/terraform/modules/cloudrun"

        render_to_file(
            f"{mod_dir}/main.tf.j2",
            ctx.project_dir / mod_dir / "main.tf",
            manifest=ctx.manifest,
        )
        render_to_file(
            f"{mod_dir}/variables.tf.j2",
            ctx.project_dir / mod_dir / "variables.tf",
            manifest=ctx.manifest,
        )
        render_to_file(
            f"{mod_dir}/outputs.tf.j2",
            ctx.project_dir / mod_dir / "outputs.tf",
            manifest=ctx.manifest,
        )
        return {}


@register_step
class WriteIamModule(BaseStep):
    step_id = "J.3_write_iam_module"
    phase = "J"
    depends_on = ["J.1_write_provider_tf"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        mod_dir = "infra/terraform/modules/iam"

        render_to_file(
            f"{mod_dir}/main.tf.j2",
            ctx.project_dir / mod_dir / "main.tf",
            manifest=ctx.manifest,
        )
        render_to_file(
            f"{mod_dir}/variables.tf.j2",
            ctx.project_dir / mod_dir / "variables.tf",
            manifest=ctx.manifest,
        )
        render_to_file(
            f"{mod_dir}/outputs.tf.j2",
            ctx.project_dir / mod_dir / "outputs.tf",
            manifest=ctx.manifest,
        )
        return {}


@register_step
class WriteSecretsModule(BaseStep):
    step_id = "J.4_write_secrets_module"
    phase = "J"
    depends_on = ["J.1_write_provider_tf"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        mod_dir = "infra/terraform/modules/secrets"

        render_to_file(
            f"{mod_dir}/main.tf.j2",
            ctx.project_dir / mod_dir / "main.tf",
            manifest=ctx.manifest,
        )
        render_to_file(
            f"{mod_dir}/variables.tf.j2",
            ctx.project_dir / mod_dir / "variables.tf",
            manifest=ctx.manifest,
        )
        return {}


@register_step
class WriteNetworkingModule(BaseStep):
    step_id = "J.5_write_networking_module"
    phase = "J"
    depends_on = ["J.1_write_provider_tf"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        mod_dir = "infra/terraform/modules/networking"

        render_to_file(
            f"{mod_dir}/main.tf.j2",
            ctx.project_dir / mod_dir / "main.tf",
            manifest=ctx.manifest,
        )
        render_to_file(
            f"{mod_dir}/variables.tf.j2",
            ctx.project_dir / mod_dir / "variables.tf",
            manifest=ctx.manifest,
        )
        return {}


@register_step
class WriteDevEnv(BaseStep):
    step_id = "J.6_write_dev_env"
    phase = "J"
    depends_on = [
        "J.2_write_cloudrun_module",
        "J.3_write_iam_module",
        "J.4_write_secrets_module",
        "J.5_write_networking_module",
    ]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        env_dir = "infra/terraform/envs/dev"

        render_to_file(
            f"{env_dir}/main.tf.j2",
            ctx.project_dir / env_dir / "main.tf",
            manifest=ctx.manifest,
        )
        render_to_file(
            f"{env_dir}/variables.tf.j2",
            ctx.project_dir / env_dir / "variables.tf",
            manifest=ctx.manifest,
        )
        render_to_file(
            f"{env_dir}/terraform.tfvars.j2",
            ctx.project_dir / env_dir / "terraform.tfvars",
            manifest=ctx.manifest,
        )
        return {}
