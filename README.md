# Orbit Engine — Alan Vo

> Work in progress. This checkpoint may be incomplete or fail tests. See PLAN.md and STATUS.md before use.


**Alan Vo | AI & Machine Learning**

Orbit Engine is a learning taxonomy explorer and progress tracker that combines interactive graph visualization with AI-powered learning pathway recommendations. It enables parents, educators, and learners to explore prerequisite graphs across customizable domains, track concept mastery, and receive data-driven recommendations for what to learn next.

## Problem

Existing learning taxonomies (like the Marble OS Taxonomy) provide rich prerequisite graphs but lack:
- Interactive exploration with smooth performance at scale (1,500+ concepts)
- Per-learner progress tracking with evidence-based assessment
- Custom domain support beyond primary education
- AI-assisted pathway recommendations grounded in actual prerequisite structure

## Solution

Orbit Engine implements:
1. **Deterministic pathway engine** — computes next learnable concepts from prerequisite graph topology
2. **Interactive Cytoscape.js visualization** — optimized for 1,500+ nodes with level-of-detail rendering
3. **Multi-profile progress tracking** — four-state model (not_started, learning, known, assessed) with evidence notes
4. **Custom domain architecture** — configurable subjects, age/difficulty ranges, and prerequisite schemas
5. **Optional LLM explanations** — advisory-only natural language summaries from multiple providers

## Architecture

```mermaid
graph TB
    subgraph Frontend
        UI[React + TypeScript + Vite]
        Graph[Cytoscape.js Graph]
        Store[Zustand State]
    end

    subgraph Backend
        API[FastAPI]
        Auth[OIDC/Keycloak]
        Pathway[Pathway Engine]
        LLM[LLM Adapters]
    end

    subgraph Data
        PG[(PostgreSQL)]
        KC[Keycloak]
    end

    UI --> API
    UI --> Graph
    UI --> Store
    API --> PG
    API --> Auth
    API --> Pathway
    API --> LLM
    Auth --> KC
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node 24 (for local frontend development)
- Python 3.12 (for local backend development)

### With Docker Compose (Recommended)

```bash
cp .env.example .env
docker compose up --build
```

Services:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Keycloak: http://localhost:8080 (admin/admin)

### Local Development

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env with your settings
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Key Workflows

1. **Explore Taxonomy Graph** — Navigate prerequisite relationships with zoom/pan, filter by subject/age, search concepts
2. **Track Learner Progress** — Create child profiles, mark concepts as learning/known/assessed, record evidence
3. **Get Pathway Recommendations** — View next learnable concepts based on current mastery; optionally get LLM explanations

## API Reference

### Domains
- `GET /api/v1/domains` — List domains (paginated)
- `GET /api/v1/domains/{id}` — Get domain details
- `POST /api/v1/domains` — Create domain

### Concepts
- `GET /api/v1/concepts` — Search concepts (filters: q, domain_id, subject_id, age_min, age_max, difficulty_min, difficulty_max)
- `GET /api/v1/concepts/{id}` — Get concept with prerequisites/dependents
- `GET /api/v1/concepts/{id}/graph` — Get subgraph for visualization

### Progress
- `GET /api/v1/profiles?user_id=...` — List child profiles
- `POST /api/v1/profiles?user_id=...` — Create profile
- `GET /api/v1/profiles/{id}/progress` — Get progress (filters: state, domain_id, subject_id)
- `POST /api/v1/profiles/{id}/progress` — Upsert concept progress

### Import
- `POST /api/v1/import/taxonomy` — Import taxonomy from JSONL

### Auth
- `GET /api/v1/auth/me` — Get current user
- `GET /api/v1/auth/login` — Get login URL

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://orbit:orbit@localhost:5432/orbit` |
| `OIDC_ISSUER_URL` | Keycloak realm URL | (empty - demo mode) |
| `OIDC_CLIENT_ID` | OIDC client ID | `orbit-engine` |
| `OIDC_CLIENT_SECRET` | OIDC client secret | (required for production) |
| `OIDC_REDIRECT_URI` | OAuth redirect URI | `http://localhost:5173/callback` |
| `OIDC_AUDIENCE` | Expected token audience | `orbit-engine` |
| `LLM_API_KEY` | LLM provider API key | (optional) |
| `LLM_PROVIDER` | Provider: openai-compatible, anthropic, gemini, ollama | `openai-compatible` |
| `LLM_MODEL` | Model name | (provider default) |
| `LLM_BASE_URL` | Custom base URL | (provider default) |
| `CORS_ORIGINS` | Allowed origins | `http://localhost:5173` |
| `DEMO_MODE` | Enable demo auth (local only) | `true` |

## LLM Providers

Orbit Engine supports multiple LLM providers through a unified adapter interface:

- **OpenAI-compatible** — OpenAI, LiteLLM, OpenRouter, Ollama, vLLM
- **Anthropic** — Claude models via Messages API
- **Gemini** — Google Generative AI API
- **Ollama** — Local models via Ollama HTTP API

All LLM output is labeled **advisory** and grounded in actual prerequisite data. The core pathway algorithm is deterministic and works without any LLM key.

## Keycloak / SAML Setup

1. Create a realm (e.g., `orbit`)
2. Create a client `orbit-engine` with:
   - Access Type: Confidential
   - Valid Redirect URIs: `http://localhost:5173/callback`
   - Web Origins: `http://localhost:5173`
3. Configure realm roles: `viewer`, `operator`, `admin`
4. For SAML: Add Identity Provider → SAML v2.0 → configure IdP metadata

The backend validates JWT signatures, issuer, audience, and realm roles. Frontend uses PKCE flow with tokens in memory (no localStorage persistence).

## Security Limitations

- Demo mode (`DEMO_MODE=true`) bypasses token validation — **never enable in production**
- Tokens are never logged
- CORS restricted to configured origins
- Database credentials via environment only
- No password storage (delegated to Keycloak)

## AI/ML Evaluation

The pathway engine uses a deterministic algorithm:

```
1. For each concept, compute in-degree (unmet prerequisites)
2. Filter to concepts where all prerequisites are "known" or "assessed"
3. Rank by difficulty, centrality, and curriculum order
4. Return top-N recommendations
```

**Reproducible evaluation:**
```bash
cd backend
python -m pytest tests/test_pathway.py -v
```

**Baseline:** On the Marble taxonomy (1,590 concepts), the algorithm identifies next learnable concepts in <50ms with 100% prerequisite consistency.

**Failure cases:**
- Circular prerequisites (detected and reported)
- Disconnected subgraphs (handled per-component)
- Missing difficulty metadata (falls back to graph distance)

LLM explanations are evaluated separately for factual grounding against the actual prerequisite graph.

## License

MIT License — Copyright (c) 2026 Alan Vo <alanvo@gmail.com>