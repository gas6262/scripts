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


class ProjectManifest(BaseModel):
    project: ProjectConfig
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    services: list[ServiceConfig] = Field(default_factory=list)
