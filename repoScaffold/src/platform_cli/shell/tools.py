"""Tool detection and install hints."""
from __future__ import annotations

import platform
import shutil

REQUIRED_TOOLS: list[dict[str, str]] = [
    {
        "name": "Google Cloud SDK",
        "cmd": "gcloud",
        "brew": "google-cloud-sdk",
        "install_hint": "brew install --cask google-cloud-sdk  (or https://cloud.google.com/sdk/docs/install)",
    },
    {
        "name": "Terraform",
        "cmd": "terraform",
        "brew": "terraform",
        "install_hint": "brew install terraform  (or https://developer.hashicorp.com/terraform/install)",
    },
    {
        "name": "Docker",
        "cmd": "docker",
        "brew": "--cask docker",
        "install_hint": "brew install --cask docker  (or https://docs.docker.com/get-docker/)",
    },
    {
        "name": "Node.js",
        "cmd": "node",
        "brew": "node",
        "install_hint": "brew install node  (or https://nodejs.org/)",
    },
    {
        "name": "npm",
        "cmd": "npm",
        "brew": "",
        "install_hint": "Installed with Node.js",
    },
    {
        "name": "MongoDB Atlas CLI",
        "cmd": "atlas",
        "brew": "mongodb-atlas-cli",
        "install_hint": "brew install mongodb-atlas-cli  (or https://www.mongodb.com/docs/atlas/cli/current/install-atlas-cli/)",
    },
]


def detect_tool(cmd: str) -> bool:
    """Return True if *cmd* is found on PATH."""
    return shutil.which(cmd) is not None


def is_macos() -> bool:
    return platform.system() == "Darwin"


def has_brew() -> bool:
    return shutil.which("brew") is not None
