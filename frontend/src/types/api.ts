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