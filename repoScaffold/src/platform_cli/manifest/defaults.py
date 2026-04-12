"""Default values applied when the manifest omits fields."""

DEFAULT_PORTS: dict[str, int] = {
    "api": 3006,
    "webapp": 3005,
    "worker": 8080,
}

DEFAULT_STACKS: dict[str, str] = {
    "api": "express",
    "webapp": "react",
    "worker": "python",
}
