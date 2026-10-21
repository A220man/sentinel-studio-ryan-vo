# Changelog

## 1.0.0 — work-in-progress checkpoint

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