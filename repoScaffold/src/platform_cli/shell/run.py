"""subprocess wrapper: ShellResult and run_cmd."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass
class ShellResult:
    command: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def run_cmd(
    cmd: str | list[str],
    *,
    cwd: str | None = None,
    check: bool = False,
    capture: bool = True,
    timeout: int = 300,
) -> ShellResult:
    """Run a shell command and return a ShellResult."""
    if isinstance(cmd, str):
        shell = True
        cmd_str = cmd
    else:
        shell = False
        cmd_str = " ".join(cmd)

    result = subprocess.run(
        cmd,
        shell=shell,
        cwd=cwd,
        capture_output=capture,
        text=True,
        timeout=timeout,
    )

    sr = ShellResult(
        command=cmd_str,
        returncode=result.returncode,
        stdout=result.stdout if capture else "",
        stderr=result.stderr if capture else "",
    )

    if check and not sr.ok:
        raise RuntimeError(
            f"Command failed (rc={sr.returncode}): {cmd_str}\n{sr.stderr}"
        )

    return sr
