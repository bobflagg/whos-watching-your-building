# Phase 0 — Foundation: Requirements

## Scope

This phase establishes the dependency baseline and environment configuration so that every subsequent phase has a consistent, reproducible starting point.

**In scope:**
- Add all project dependencies to `pyproject.toml` via `uv add`
- Create `.env.example` documenting every required secret and config value

**Out of scope:**
- Neo4j Desktop installation or connection (Phase 0 does not require Neo4j to be running)
- Smoke-test scripts that exercise live services
- Any data ingestion or exploration

## Decisions

**uv is the canonical package manager for this project.**
All dependency changes go through `uv add` / `uv remove`. Do not use `pip install` directly. `uv.lock` is committed so environments are reproducible across machines.

**Python 3.13+ is required.**
Already pinned in `pyproject.toml`. Do not lower this constraint.

**Secrets are managed via `.env` + `python-dotenv`.**
`.env` is gitignored and never committed. `.env.example` is committed and kept in sync with every key the application reads. No secrets in code or config files.

**This phase is local development only.**
No CI, no cloud deployment, no remote services are required or configured here.

## Context

The project's Python environment has already been initialized with `uv`. The `pyproject.toml` currently only lists `streamlit`. All other dependencies identified in the tech stack need to be added before later phases can proceed.
