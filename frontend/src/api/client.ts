// Typed API client for Sentinel Studio backend

import type { CompressRequest, CompressResponse, HealthResponse } from "../types/api";

const API_BASE = "/api/v1";

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  health: {
    check: () => fetchJson<HealthResponse>("/health"),
    ready: () => fetchJson<HealthResponse>("/health/ready"),
  },

  compress: {
    single: (request: CompressRequest) =>
      fetchJson<CompressResponse>(`${API_BASE}/compress`, {
        method: "POST",
        body: JSON.stringify(request),
      }),

    batch: (requests: CompressRequest[]) =>
      fetchJson<CompressResponse[]>(`${API_BASE}/compress/batch`, {
        method: "POST",
        body: JSON.stringify(requests),
      }),
  },
};