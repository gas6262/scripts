"""Custom Jinja2 filters: snake_case, kebab_case, env_var."""
from __future__ import annotations

import re


def snake_case(value: str) -> str:
    s = re.sub(r"[\s\-]+", "_", value)
    s = re.sub(r"([A-Z])", r"_\1", s).lower()
    return re.sub(r"_+", "_", s).strip("_")


def kebab_case(value: str) -> str:
    s = re.sub(r"[\s_]+", "-", value)
    s = re.sub(r"([A-Z])", r"-\1", s).lower()
    return re.sub(r"-+", "-", s).strip("-")


def env_var(value: str) -> str:
    return snake_case(value).upper()
