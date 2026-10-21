# Deployment Guide

## Prerequisites

- Docker 24+ and Docker Compose 2+
- Or: Python 3.12+, Node 24+, Keycloak 26+

## Quick Start (Docker Compose)

```bash
# Build and start all services
docker compose up --build -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

Services:
| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://127.0.0.1:5173 | React dashboard |
| Backend API | http://127.0.0.1:8000 | FastAPI server |
| Keycloak | http://127.0.0.1:8080 | OIDC identity provider |

## Environment Variables

Create `.env` from `.env.example`:

```bash
cp .env.example .env
# Edit .env with your values
```

Key variables:
- `LLM_API_KEY`: Required for LLM features (optional for core compression)
- `LLM_PROVIDER`: openai-compatible, anthropic, gemini, ollama
- `LLM_MODEL`: Model identifier
- `LLM_BASE_URL`: Custom endpoint (for Ollama, LiteLLM, OpenRouter)
- `DATABASE_URL`: SQLite path (default: ./data/sentinel.db)
- `CORS_ORIGINS`: Comma-separated allowed origins

## Production Deployment

### 1. Reverse Proxy (Required)

Deploy nginx/Traefik/Caddy in front for:
- TLS termination
- Rate limiting
- Authentication integration
- Static asset caching

### 2. Database

SQLite is development-only. For production:

```yaml
# docker-compose.override.yml
services:
  backend:
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/sentinel
    depends_on:
      - db

  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=sentinel
      - POSTGRES_USER=sentinel
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
```

### 3. Keycloak Production

- Use external PostgreSQL for Keycloak
- Set strong admin password
- Configure realm with production clients
- Enable HTTPS in Keycloak
- Use proper certificates

### 4. Secrets Management

Never commit secrets. Use:
- Docker secrets
- HashiCorp Vault
- Cloud provider secret managers
- GitOps sealed secrets

### 5. Monitoring

Add health check endpoints to load balancer:
- `/health` - liveness
- `/health/ready` - readiness

## Scaling

### Backend

- Run multiple uvicorn workers: `uvicorn app.main:app --workers 4`
- Use PostgreSQL for shared state
- Add Redis for caching (future)

### Frontend

- Static files served by nginx/CDN
- No scaling needed for SPA

### Keycloak

- Cluster mode for HA
- External database required

## Backup Strategy

### Automated Backups

```bash
#!/bin/bash
# backup.sh - run via cron
DATE=$(date +%Y%m%d-%H%M%S)
docker exec sentinel-backend sqlite3 /app/data/sentinel.db ".backup /backup/sentinel-$DATE.db"
# Upload to S3/GCS/etc.
```

### Keycloak

Export realm weekly:
```bash
docker exec keycloak /opt/keycloak/bin/kc.sh export --dir /opt/keycloak/data/backup --realm sentinel-studio
```

## Troubleshooting

### Backend Won't Start

```bash
# Check logs
docker compose logs backend

# Common issues:
# - Port 8000 in use
# - Database permission (check volume ownership)
# - Missing LLM_API_KEY (only needed for LLM features)
```

### Frontend Build Fails

```bash
# Check Node version
node --version  # Should be 24+

# Clear cache
cd frontend && rm -rf node_modules package-lock.json && npm install
```

### Keycloak Not Ready

```bash
# Check logs
docker compose logs keycloak

# Increase start_period in docker-compose.yaml
# Check dev-file database permissions
```

## Security Checklist

- [ ] Change Keycloak admin password
- [ ] Change Keycloak client secret
- [ ] Use strong DATABASE_URL password
- [ ] Enable TLS on reverse proxy
- [ ] Restrict CORS_ORIGINS to production domains
- [ ] Set DEBUG=false
- [ ] Rotate LLM_API_KEY periodically
- [ ] Enable audit logging
- [ ] Configure firewall rules