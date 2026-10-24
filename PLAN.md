# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

compression-history

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

Status: done

Acceptance:
- Expose compress tool via MCP protocol
- Works with Claude Desktop / MCP clients

Implementation: `backend/app/mcp/server.py`, `backend/app/mcp/__init__.py`

Tests: `backend/tests/test_mcp.py`

### compression-history — Compression History & Analytics

Status: done

Acceptance:
- Persist compression operations to SQLite with metadata
- API endpoints for history listing with filtering and pagination
- Analytics summary endpoint (totals, by type, by algorithm)
- Frontend History panel with table view and analytics summary
- Clear history functionality

Implementation: `backend/app/models/schemas.py (updated)`, `backend/app/services/history.py`, `backend/app/services/compression.py (updated)`, `backend/app/api/history.py`, `backend/app/main.py (updated)`, `frontend/src/components/HistoryPanel.tsx`, `frontend/src/components/HistoryPanel.css`, `frontend/src/api/client.ts (updated)`, `frontend/src/types/api.ts (updated)`, `frontend/src/App.tsx`, `frontend/src/main.tsx (updated)`, `frontend/src/styles/main.css (updated)`

Tests: `backend/tests/test_history.py`, `frontend/src/components/HistoryPanel.test.tsx`

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

