# Architecture Documentation

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Sentinel Studio                         │
├─────────────────┬─────────────────────┬─────────────────────┤
│   Frontend      │      Backend        │    Compression      │
│   (React)       │     (FastAPI)       │      Engine         │
├─────────────────┼─────────────────────┼─────────────────────┤
│ • Dashboard     │ • REST API          │ • JSON Dedup        │
│ • API Client    │ • Health Checks     │ • Text Minify       │
│ • TypeScript    │ • Pydantic Models   │ • Token Counting    │
└────────┬────────┴──────────┬──────────┴──────────┬───────────┘
         │                   │                     │
         └───────────────────┴─────────────────────┘
                            │
                    ┌───────▼───────┐
                    │   Keycloak    │
                    │   (OIDC)      │
                    └───────────────┘
```

## Components

### Frontend (React + TypeScript + Vite)

- **CompressionPanel**: Main dashboard component
- **CompressionResult**: Output display with stats and actions
- **api/client.ts**: Typed API client using fetch
- **types/api.ts**: TypeScript interfaces for API contracts

### Backend (FastAPI)

- **app/main.py**: Application factory, lifespan, CORS
- **app/api/compress.py**: Compression endpoints
- **app/api/health.py**: Health check endpoints
- **app/core/compression.py**: Core algorithms
- **app/core/config.py**: Settings management
- **app/cli.py**: CLI entrypoint

### Compression Engine

#### JSON Deduplication

1. Parse JSON input
2. Extract all string values recursively
3. Build dictionary of unique strings (index → value)
4. Replace strings >12 chars with `§XX§` references
5. Serialize with minimal whitespace
6. If dictionary saves tokens, wrap as `{"$dict": {...}, "$data": ...}`

#### Text Minification

1. Split into lines
2. Remove trailing whitespace from each line
3. Collapse consecutive blank lines to single blank line
4. Remove full-line comments (// or #) without meaningful text
5. Rejoin with newlines

#### Token Counting

Uses tiktoken (cl100k_base encoding) for accurate token estimates. Falls back to ~4 chars/token if unavailable.

## Data Flow

```
Input (JSON/Text)
      │
      ▼
Auto-detect content type
      │
      ├── JSON ──► compress_json ──► Output + Stats
      │
      └── Text ──► compress_text ──► Output + Stats
```

## Deployment

### Development

```bash
# Backend
cd backend && .venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Frontend
cd frontend && npm run dev
```

### Production (Docker Compose)

```bash
docker compose up --build -d
```

Services:
- Frontend: http://127.0.0.1:5173 (nginx)
- Backend: http://127.0.0.1:8000 (uvicorn)
- Keycloak: http://127.0.0.1:8080

### TLS Reverse Proxy

Required for production. Example nginx config:

```nginx
server {
    listen 443 ssl http2;
    server_name sentinel.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Backup/Restore

### Database (SQLite)

```bash
# Backup
cp backend/data/sentinel.db backup/sentinel-$(date +%Y%m%d).db

# Restore
cp backup/sentinel-20261021.db backend/data/sentinel.db
```

### Keycloak

Keycloak uses dev-file database. Export realm:

```bash
docker exec keycloak /opt/keycloak/bin/kc.sh export --dir /opt/keycloak/data/export --realm sentinel-studio
```

## IdP Enrollment (SAML)

Keycloak supports SAML identity brokering:

1. In Keycloak admin console: Identity Providers → Add SAML v2.0
2. Configure SAML entity ID, SSO URL, certificate
3. Map SAML attributes to Keycloak user attributes
4. Add identity provider to "sentinel-frontend" client authentication flow

See Keycloak documentation for detailed SAML broker setup.