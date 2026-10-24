# Changelog

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.2.0 — 2026-10-24

### Added
- Compression history persistence with SQLite backend
- History API: `GET /api/v1/history` with filtering (content_type, algorithm, min_ratio, date range) and pagination
- Analytics API: `GET /api/v1/history/analytics` with totals, by content type, by algorithm
- Clear history API: `DELETE /api/v1/history`
- Frontend History panel with tabbed navigation (Compress / History)
- Analytics summary cards (total compressions, tokens saved, average reduction)
- Sortable, filterable history table with content preview
- 11 new backend tests for history service and API
- 5 new frontend tests for HistoryPanel component
- Updated compression service to automatically record operations

### Changed
- Updated `backend/app/models/schemas.py` with history/analytics models
- Updated `backend/app/services/compression.py` to record history
- Updated `backend/app/main.py` to include history router
- Updated `frontend/src/api/client.ts` with history endpoints
- Updated `frontend/src/types/api.ts` with history types
- Refactored frontend to use App component with tab navigation
- Updated `frontend/src/styles/main.css` with app layout styles

## 1.1.0 — 2026-10-24

### Added
- MCP (Model Context Protocol) server exposing compression tools
- Tools: `compress_json`, `compress_text`, `compress_auto`, `decompress_json`, `compress_batch`
- Compatible with Claude Desktop and other MCP clients
- 12 new backend tests for MCP server functionality
- FastMCP high-level API integration

### Changed
- Upgraded FastAPI to 0.162.0 for starlette 1.10 compatibility


Partial code published for continued development. Known issues: STATUS.md.

All notable changes to Sentinel Studio are documented here.

## [1.0.0] - 2026-10-21

### Added
- Core compression engine with JSON deduplication and text minification
- Python library: `compress_auto`, `compress_json`, `compress_text`, `decompress_json`
- CLI: `sentinel compress` / `sentinel decompress` with `--show-stats`
- FastAPI server with `/api/v1/compress` and `/api/v1/compress/batch` endpoints
- Health checks: `/health`, `/health/ready`
- React dashboard with side-by-side compression view
- Token counting via tiktoken (cl100k_base)
- Deterministic algorithms, no LLM required
- Comprehensive test suite (34 backend, 9 frontend tests)
- Docker Compose with frontend, backend, Keycloak
- Auto-detection of JSON vs text content

### Security
- LLM API keys server-side only
- CORS restricted to configured origins
- No authentication in v1.0.0 (planned for v1.1.0)

### Known Limitations
- SQLite only (no PostgreSQL support yet)
- No authentication/authorization
- No rate limiting
- Dictionary-based JSON decompression only works when dictionary was emitted
- Demo mode not implemented

