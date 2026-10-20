# Changelog

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-10-20

### Added
- Initial project skeleton with FastAPI backend and React frontend
- SQLAlchemy models for domains, subjects, concepts, prerequisites, child profiles, progress
- REST API for domains, concepts (search, detail, graph), progress tracking
- JSONL taxonomy import endpoint
- OIDC authentication with Keycloak (PKCE flow)
- Interactive graph visualization with Cytoscape.js
- Child profile management with four-state progress tracking
- Search and filter UI (subject, age, difficulty, known-state filters)
- Docker Compose with PostgreSQL, Keycloak, backend, frontend
- Backend tests: health, domains, concepts, progress, auth, import, filtering (12+ tests)
- Frontend tests: LoginPage, ExplorerPage (3+ tests)
- MIT License, README with architecture diagram and API reference