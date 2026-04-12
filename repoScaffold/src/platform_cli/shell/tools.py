"""Tool detection and install hints."""
from __future__ import annotations

import shutil

REQUIRED_TOOLS: list[dict[str, str]] = [
    {
        "name": "Google Cloud SDK",
        "cmd": "gcloud",
        "install_hint": "https://cloud.google.com/sdk/docs/install",
    },
    {
        "name": "Terraform",
        "cmd": "terraform",
        "install_hint": "brew install terraform  (or https://developer.hashicorp.com/terraform/install)",
    },
    {
        "name": "Docker",
        "cmd": "docker",
        "install_hint": "https://docs.docker.com/get-docker/",
    },
    {
        "name": "Node.js",
        "cmd": "node",
        "install_hint": "brew install node  (or https://nodejs.org/)",
    },
    {
        "name": "npm",
        "cmd": "npm",
        "install_hint": "Installed with Node.js",
    },
    {
        "name": "MongoDB Atlas CLI",
        "cmd": "atlas",
        "install_hint": "brew install mongodb-atlas-cli  (or https://www.mongodb.com/docs/atlas/cli/current/install-atlas-cli/)",
    },
]


def detect_tool(cmd: str) -> bool:
    """Return True if *cmd* is found on PATH."""
    return shutil.which(cmd) is not None
