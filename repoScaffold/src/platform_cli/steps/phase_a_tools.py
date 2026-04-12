"""Phase A: Tool detection and installation steps."""
from __future__ import annotations

from typing import Any

from platform_cli.engine.context import ScaffoldContext
from platform_cli.engine.registry import register_step
from platform_cli.engine.step import BaseStep
from platform_cli.shell.tools import REQUIRED_TOOLS, detect_tool


@register_step
class DetectToolsStep(BaseStep):
    step_id = "A.1_detect_tools"
    phase = "A"
    depends_on: list[str] = []

    def inputs(self):
        return ["PATH environment"]

    def outputs_spec(self):
        return ["detected_tools map"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        results: dict[str, bool] = {}
        for tool in REQUIRED_TOOLS:
            results[tool["cmd"]] = detect_tool(tool["cmd"])
        ctx.set("detected_tools", results)
        return {"detected_tools": results}


@register_step
class InstallToolsStep(BaseStep):
    step_id = "A.2_install_tools"
    phase = "A"
    depends_on = ["A.1_detect_tools"]

    def run(self, ctx: ScaffoldContext) -> dict[str, Any]:
        detected = ctx.get("detected_tools", {})
        missing = [
            t for t in REQUIRED_TOOLS if not detected.get(t["cmd"], False)
        ]
        if missing:
            from rich.console import Console
            console = Console()
            console.print("[yellow]Missing tools (install manually):[/yellow]")
            for t in missing:
                console.print(f"  - {t['name']}: {t['install_hint']}")
        return {"missing_tools": [t["cmd"] for t in missing]}
