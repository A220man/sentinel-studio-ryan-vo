// Typed API client for Sentinel Studio backend

import type {
  CompressRequest,
  CompressResponse,
  HealthResponse,
  HistoryResponse,
  AnalyticsSummary,
  HistoryQueryParams,
} from "../types/api";

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

function buildQuery(params: HistoryQueryParams): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      searchParams.append(key, String(value));
    }
  });
  const query = searchParams.toString();
  return query ? `?${query}` : "";
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

  history: {
    list: (params: HistoryQueryParams = {}) =>
      fetchJson<HistoryResponse>(`${API_BASE}/history${buildQuery(params)}`),

    analytics: () =>
      fetchJson<AnalyticsSummary>(`${API_BASE}/history/analytics`),

    clear: () =>
      fetchJson<{ deleted: number }>(`${API_BASE}/history`, {
        method: "DELETE",
      }),
  },
};

