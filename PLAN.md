# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

project-skeleton

## Roadmap

### project-skeleton — FastAPI + React project skeleton with Docker

Status: in_progress

Acceptance:
- Backend FastAPI app runs with health endpoint
- Frontend Vite React app builds and serves
- Docker Compose starts backend, frontend, Keycloak, and PostgreSQL
- Preflight script passes basic checks

### taxonomy-data-model — Taxonomy data model and import pipeline

Status: planned

Acceptance:
- SQLAlchemy models for concepts, prerequisites, subjects, domains
- JSONL import script loads sample taxonomy data
- API endpoints for concepts, search, and graph traversal

### graph-visualization — Interactive graph visualization with Cytoscape.js

Status: planned

Acceptance:
- React component renders taxonomy graph
- Zoom/pan works smoothly with 1500+ nodes
- Node click shows concept details panel
- Prerequisite edges displayed

### learning-tracker — Child learning progress tracker

Status: planned

Acceptance:
- Per-child profiles with concept states (not_started, learning, known, assessed)
- Progress persistence via API
- Filters: dim known, hide known, show only known
- Search by subject, age, concept name

### oidc-auth — OIDC authentication with Keycloak

Status: planned

Acceptance:
- Backend validates Keycloak tokens
- Frontend PKCE login flow
- Role-based access (viewer, operator, admin)
- Protected API endpoints

### custom-domains — Custom domain support for taxonomy

Status: planned

Acceptance:
- Schema supports configurable subjects/domains/difficulty
- API to load/switch taxonomy datasets
- UI to manage custom domains

### ai-pathway-engine — AI-powered learning pathway recommendations

Status: planned

Acceptance:
- Deterministic algorithm finds next learnable concepts
- Optional LLM explanations for recommendations
- Provider-agnostic LLM adapter (OpenAI-compatible, Anthropic, Gemini, Ollama)
- Advisory labels on AI output

