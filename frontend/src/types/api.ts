// Type definitions for API responses

export interface CompressRequest {
  content: string;
  content_type?: "json" | "text" | "auto";
  aggressive?: boolean;
}

export interface CompressResponse {
  compressed: string;
  original_tokens: number;
  compressed_tokens: number;
  reduction_ratio: number;
  algorithm: string;
}

export interface HealthResponse {
  status: string;
  service: string;
}

export interface CompressionRecord {
  id: string;
  timestamp: string;
  content_type: string;
  algorithm: string;
  original_tokens: number;
  compressed_tokens: number;
  reduction_ratio: number;
  aggressive: boolean;
  content_preview: string;
}

export interface HistoryResponse {
  items: CompressionRecord[];
  total: number;
  limit: number;
  offset: number;
}

export interface AnalyticsSummary {
  total_compressions: number;
  total_original_tokens: number;
  total_compressed_tokens: number;
  average_reduction_ratio: number;
  by_content_type: Record<string, number>;
  by_algorithm: Record<string, number>;
}

export interface HistoryQueryParams {
  limit?: number;
  offset?: number;
  content_type?: string;
  algorithm?: string;
  min_ratio?: number;
  since?: string;
  until?: string;
}

