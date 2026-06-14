"""Pydantic models for the project manifest."""
from __future__ import annotations

from pydantic import BaseModel, Field


class CloudConfig(BaseModel):
    provider: str = "gcp"
    region: str = "us-central1"
    project_id: str = ""


class ProjectConfig(BaseModel):
    name: str
    env: str = "dev"
    cloud: CloudConfig = Field(default_factory=CloudConfig)


class DatabaseConfig(BaseModel):
    type: str = "mongodb"
    atlas_cluster: str = "Cluster0"
    db_name: str = ""


class ServiceConfig(BaseModel):
    type: str  # api | webapp | worker
    enabled: bool = True
    name: str = ""
    subdomain: str = ""
    stack: str = ""
    port: int = 0
    gpu: str = "none"
    # Worker-only: cron schedule (Cloud Scheduler format)
    # Default: every 10 minutes
    schedule: str = "*/10 * * * *"
    # Worker-only: max parallel task instances per scheduled run
    parallelism: int = 1
    # Worker-only: max execution time per task (seconds)
    timeout_seconds: int = 600


class AgentRoleConfig(BaseModel):
    name: str                    # e.g. "developer", "reviewer", "ops"
    sleep_seconds: int = 600     # seconds between iterations
    max_turns: int = 1000        # max Claude turns per iteration


class AgentConfig(BaseModel):
    service_accounts: list[str] = Field(default_factory=list)
    roles: list[AgentRoleConfig] = Field(default_factory=list)


class LinearConfig(BaseModel):
    enabled: bool = False
    workspace: str = ""      # e.g. "ai4us"
    team_key: str = ""       # e.g. "AI4" — the prefix for issue IDs
    team_name: str = ""      # e.g. "AI4US Team"


class ProjectManifest(BaseModel):
    project: ProjectConfig
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    services: list[ServiceConfig] = Field(default_factory=list)
    agents: AgentConfig = Field(default_factory=AgentConfig)
    linear: LinearConfig = Field(default_factory=LinearConfig)
