# API Documentation

## Base URL

- Development: `http://127.0.0.1:8000`
- Production: Configure reverse proxy

## Endpoints

### Health Checks

#### GET /health

Returns service health status.

**Response (200):**
```json
{
  "status": "healthy",
  "service": "sentinel-studio"
}
```

#### GET /health/readiness

Returns service readiness for Kubernetes.

**Response (200):**
```json
{
  "status": "ready",
  "service": "sentinel-studio"
}
```

### Compression

#### POST /api/v1/compress

Compress a single piece of content.

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| content | string | Yes | Content to compress |
| content_type | string | No | "auto", "json", or "text" (default: "auto") |
| aggressive | boolean | No | Enable aggressive JSON deduplication (default: true) |

**Response (200):**
| Field | Type | Description |
|-------|------|-------------|
| compressed | string | Compressed content |
| original_tokens | integer | Approximate token count of original |
| compressed_tokens | integer | Approximate token count of compressed |
| reduction_ratio | float | Fraction reduced (0.0 to 1.0) |
| algorithm | string | Algorithm used ("json-dedup", "text-smart", "json-fallback") |

**Example Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/compress \
  -H "Content-Type: application/json" \
  -d '{
    "content": "{\"items\": [{\"name\": \"foo\"}, {\"name\": \"foo\"}]}",
    "content_type": "json",
    "aggressive": true
  }'
```

**Example Response:**
```json
{
  "compressed": "{\"items\":[{\"name\":\"§00§\"},{\"name\":\"§00§\"}]}",
  "original_tokens": 46,
  "compressed_tokens": 34,
  "reduction_ratio": 0.2609,
  "algorithm": "json-dedup"
}
```

#### POST /api/v1/compress/batch

Compress multiple items in one request.

**Request Body:** Array of compress request objects

**Response (200):** Array of compress response objects

**Example Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/compress/batch \
  -H "Content-Type: application/json" \
  -d '[
    {"content": "{\"a\": 1}", "content_type": "json"},
    {"content": "function foo() { return 42; }", "content_type": "text"}
  ]'
```

### Error Responses

| Status | Description |
|--------|-------------|
| 400 | Invalid request (malformed JSON, empty content) |
| 422 | Validation error (missing required fields) |
| 500 | Internal server error |

Error format:
```json
{
  "detail": "Error description"
}
```

## Python Client Usage

```python
import httpx

client = httpx.Client(base_url="http://127.0.0.1:8000")

# Single compression
response = client.post("/api/v1/compress", json={
    "content": '{"items": [{"name": "foo"}, {"name": "foo"}]}',
    "content_type": "json"
})
result = response.json()
print(f"Reduced by {result['reduction_ratio']:.1%}")

# Batch compression
response = client.post("/api/v1/compress/batch", json=[
    {"content": "item1", "content_type": "text"},
    {"content": "item2", "content_type": "text"}
])
results = response.json()
```

## Compression Algorithms

### json-dedup

For JSON with repeated string values. Extracts unique strings into a dictionary, replaces occurrences with `§XX§` references. Best for API responses, config files, structured logs.

### text-smart

For source code and plain text. Removes trailing whitespace, collapses multiple blank lines, removes redundant full-line comments. Best for code, logs, documentation.

### json-fallback

Used when content_type=json but input is invalid JSON. Falls back to text-smart.

### auto

Inspects input: if it starts with `{` or `[` and parses as JSON, uses json-dedup; otherwise uses text-smart.