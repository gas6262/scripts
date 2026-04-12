Create an opinionated Python-based CLI that scaffolds, provisions, tests, and deploys a full-stack application platform end-to-end on GCP for a development environment.

## Goal

Build a highly modular, readable, agent-friendly CLI that can create a new project from scratch and get it working end-to-end with minimal manual steps. The CLI must be designed so that either a human or coding agent can safely inspect, extend, and iterate on it.

The CLI should favor reusing existing mature CLIs and tools whenever possible rather than reimplementing behavior from scratch.

The primary command should be:

```bash
platform-cli scaffold <project-name> [options]
```

The CLI should also support:

```bash
platform-cli install # Install all dependencies and CLIs needed
platform-cli test <service> # Test specific service
```

## Core Requirements

### 1. Language / Architecture

* CLI must be Python-based.
* Use a modular architecture with clear package boundaries.
* Code must be highly readable and easy for agents to modify.
* Every major action must be implemented as an independent step/task.
* Steps must be resumable, skippable, and idempotent.
* Use a DAG / graph execution model for scaffold steps.
* Every step should define:

  * inputs
  * outputs
  * dependencies
  * retry behavior

### 2. Development Environment (v1 scope)

* Only support dev environment initially.
* Everything must work locally first.
* Generated local setup must work with developer credentials.
* Local apps can run outside Docker for fast iteration.

### 3. Opinionated Defaults

#### Local Ports

* Frontend always runs on localhost:3005
* API always runs on localhost:3006
* Docker containers should expose port 80 externally wherever practical.

#### Cloud

* GCP is required. However, it should still use Terraform for config-driven infrastructure
* All deployable services should run on Cloud Run or Cloud Run Jobs / Functions where appropriate.
* Strong preference for Docker containerization everywhere.

### 4. Project Manifest (Source of Truth)

Generate a manifest file that defines the full project:

Example:

```yaml
project:
  name: MyApp
  env: dev
  cloud:
    provider: gcp
    region: us-central1
    project_id: MyApp # Should default to project name

database:
  type: mongodb
  atlas_cluster: Cluster0
  db_name: my_app

services:
  - type: api
    enabled: true
    name: api
    subdomain: api # should be automatic based 
    stack: express
    port: 3006 # API should default to 3006

  - type: webapp
    enabled: true
    name: app
    subdomain: app # default to name
    stack: react
    port: 3005 # Web should default to 3005

  - type: worker # Should use Cloud run function by default
    enabled: false
    gpu: optional
```

This manifest must drive all generated artifacts.

## Required Scaffold Scope

## Phase A: Bootstrap / Tooling

### Tool Detection / Installation

CLI should detect / install:

* gcloud CLI
* terraform
* docker
* mongodb atlas CLI (if MongoDB selected)
* node / npm if needed

This is a separate install command. User should download ALL tooling as a prerequisite rather than autodetection. Must provide clear instructions if installation requires user approval.

## Phase B: Repo / Folder Scaffold

Generate:

```text
project/
  cli/
  services/
    api/
        src/
        DockerFile
        .env
        ...
    web/
    worker/
  infra/
    terraform/
      modules/
      envs/dev/
  cloudbuild/
    terraform.yaml # If necessary
    api.yaml
    web.yaml
  cloudrun/
    api.yaml
    web.yaml
  .vscode/
  .claude/
  AGENTS.md
  .env.example
  .gitignore
  docker-compose.yml
  project.manifest.yaml
```

### Additional Files

Must generate:

* AGENTS.md with architecture + conventions
* .claude config / guidance
* .vscode launch/tasks for local run/test
* README with setup steps

## Phase C: Database Setup

### MongoDB Atlas Support (initial DB support)

If DB type = mongodb:

CLI should:

* authenticate with Atlas CLI
* select org / project
* inspect Cluster0
* create DB if missing
* skip if exists
* create dummy collection: items
* insert seed rows / docs

Example seed:

```json
[{"name": "example item"}]
```

### DB Credentials

After DB setup:

* generate connection string
* store locally in a local secrets manifest such as .env
* then store in GCP Secret Manager for the project
* maintain secrets manifest

Secret sync should be idempotent.

## Phase D: API Scaffold

### Initial API Support

Support only:

* Node.js Express API

If DB = MongoDB:

* auto-add Mongoose
* create DB connection layer
* create model for items

Generated API must include:

* GET /items

Requirements:

* API works immediately locally.
* API reads credentials from env.
* proper folder structure.
* lint config.
* Dockerfile.

### Docker Requirements

* every service dockerized.
* API Dockerfile maps to port 80.
* Dockerfiles should follow best practices.

## Phase E: Frontend Scaffold

Initial support:

* React

Requirements:

* reuse standard scaffold CLI if possible.
* homepage loads.
* can fetch /items.
* local runs on 3005.
* Dockerfile.

Frontend should not need knowledge of API implementation details.
Only use configured endpoint contracts (initially /items).

## Phase F: Worker Scaffold

Requirements:

* Cloud Run compatible.
* optional GPU support config.
* scaffold stub worker.
* dockerized.

## Phase G: GCP Setup

CLI should support:

* create or connect GCP project
* enable required APIs:
  * Cloud Run
  * Cloud Build
  * Secret Manager
  * Artifact Registry
* create Artifact Registry repo
* create service accounts
* configure IAM minimally

Must clearly separate:

* build service account
* runtime service account

## Phase H: Secret Manager

Create a secret registry system.

Requirements:

* secret manifest file
* sync local env -> GCP Secret Manager
* generate .env.example comments for secret-backed vars
* never commit local secrets

## Phase I: Cloud Build

Generate Cloud Build configs for:

* api build / deploy
* web build / deploy
* terraform rollout

Requirements:

* Cloud Build injects secrets from Secret Manager
* service builds are modular
* Terraform has ONE dedicated pipeline

## Phase J: Terraform

Generate Terraform for:

* Cloud Run services
* IAM
* secret access
* networking basics if needed

Requirements:

* modular TF structure
* dev environment only initially
* single Terraform Cloud Build pipeline
* Terraform references generated Cloud Run configs where useful

## Phase K: Testing

CLI test command must support:

### API tests

* lint
* local start
* health check
* GET /items
* docker build test
* docker run smoke test

### Frontend tests

* local start
* page load smoke test

### Infra tests

* terraform validate
* terraform plan

### Overall

* clear logs
* fail fast
* retry support

## Quality Constraints

* prioritize correctness over speed
* highly modular and extensible
* no tightly coupled assumptions
* services communicate via contracts only
* every generated file should be production-sensible even if dev-first
* generated code should be clean and not toy quality

## Important Build Strategy

Do NOT try to make everything perfect in one pass.
Instead:

* scaffold a clean first version
* run local validations automatically
* detect failures
* iteratively fix generated code until:
  * local API works
  * DB connects
  * /items returns data
  * docker builds succeed

The CLI itself should be designed to support this iterative agent workflow.

## Deliverables

Build:

* the Python CLI codebase
* generated project template system
* all config files
* tests
* docs

Focus on making the CLI itself robust, modular, and easy to evolve.
