"""Jinja2 environment + render_to_file helper."""
from __future__ import annotations

from pathlib import Path

import jinja2

from platform_cli.templates.filters import snake_case, kebab_case, env_var

# Templates live in repoScaffold/templates/ (sibling of src/)
_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "templates"

_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(_TEMPLATES_DIR)),
    keep_trailing_newline=True,
    trim_blocks=True,
    lstrip_blocks=True,
)
_env.filters["snake_case"] = snake_case
_env.filters["kebab_case"] = kebab_case
_env.filters["env_var"] = env_var


def render_template(template_name: str, **kwargs) -> str:
    """Render a .j2 template to a string."""
    tmpl = _env.get_template(template_name)
    return tmpl.render(**kwargs)


def render_to_file(template_name: str, dest: Path, **kwargs) -> None:
    """Render a .j2 template and write it to *dest*."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_template(template_name, **kwargs))
