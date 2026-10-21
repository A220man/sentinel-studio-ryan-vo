# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

core-compression-engine

## Roadmap

### core-compression-engine — Core Compression Engine

Status: done

Acceptance:
- Compress JSON input by 60-95% with token-count preservation
- Compress plain text/code by 20% with semantic preservation
- Deterministic offline algorithm, no LLM required
- Exported as Python library with CLI entrypoint

Implementation: `backend/app/core/compression.py`, `backend/app/cli.py`, `backend/app/models/schemas.py`, `backend/app/services/compression.py`

Tests: `backend/tests/test_compression.py`, `backend/tests/test_cli.py`

### fastapi-proxy — FastAPI Proxy Server

Status: done

Acceptance:
- Accept POST /compress with JSON/text payload
- Return compressed output with metadata (ratio, tokens saved)
- Health check endpoint

Implementation: `backend/app/main.py`, `backend/app/api/compress.py`, `backend/app/api/health.py`, `backend/app/core/config.py`

Tests: `backend/tests/test_api.py`

### react-dashboard — React Compression Dashboard

Status: done

Acceptance:
- Paste/code upload input, see compressed output side-by-side
- Show compression ratio, token savings, before/after preview
- Copy/download compressed result

Implementation: `frontend/src/components/CompressionPanel.tsx`, `frontend/src/components/CompressionResult.tsx`, `frontend/src/components/CompressionPanel.css`, `frontend/src/api/client.ts`, `frontend/src/types/api.ts`, `frontend/src/main.tsx`

Tests: `frontend/src/components/CompressionPanel.test.tsx`

### mcp-server — MCP Server Integration

Status: planned

Acceptance:
- Expose compress tool via MCP protocol
- Works with Claude Desktop / MCP clients

### auth-oidc — OIDC/Keycloak Authentication

Status: planned

Acceptance:
- Authorization code flow with PKCE
- Role-based access (viewer/operator/admin)
- Session management with HttpOnly cookies

### docker-compose — Docker Compose with Keycloak

Status: done

Acceptance:
- Backend, frontend, Keycloak services
- Persistent volumes for DB and Keycloak
- Healthchecks on all services

Implementation: `docker-compose.yaml`, `backend/Dockerfile`, `frontend/Dockerfile`, `frontend/nginx.conf`, `keycloak/realm-export.json`

