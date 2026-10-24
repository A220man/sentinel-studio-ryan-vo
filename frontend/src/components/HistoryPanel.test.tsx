/// <reference types="vitest/globals" />
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { HistoryPanel } from "./HistoryPanel";

// Mock the API client
vi.mock("../api/client", () => ({
  api: {
    history: {
      list: vi.fn(),
      analytics: vi.fn(),
      clear: vi.fn(),
    },
  },
}));

import { api } from "../api/client";

describe("HistoryPanel", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders loading state initially", () => {
    (api.history.list as vi.Mock).mockResolvedValue({ items: [], total: 0, limit: 50, offset: 0 });
    (api.history.analytics as vi.Mock).mockResolvedValue({
      total_compressions: 0,
      total_original_tokens: 0,
      total_compressed_tokens: 0,
      average_reduction_ratio: 0,
      by_content_type: {},
      by_algorithm: {},
    });

    render(<HistoryPanel />);

    expect(screen.getByText("Loading history...")).toBeInTheDocument();
  });

  it("renders empty state when no history", async () => {
    (api.history.list as vi.Mock).mockResolvedValue({ items: [], total: 0, limit: 50, offset: 0 });
    (api.history.analytics as vi.Mock).mockResolvedValue({
      total_compressions: 0,
      total_original_tokens: 0,
      total_compressed_tokens: 0,
      average_reduction_ratio: 0,
      by_content_type: {},
      by_algorithm: {},
    });

    render(<HistoryPanel />);

    await waitFor(() => {
      expect(screen.getByText(/No compression history yet/i)).toBeInTheDocument();
    });
  });

  it("renders history records in table", async () => {
    const mockHistory = {
      items: [
        {
          id: "1",
          timestamp: "2024-01-15T10:30:00Z",
          content_type: "json",
          algorithm: "json-dedup",
          original_tokens: 100,
          compressed_tokens: 30,
          reduction_ratio: 0.7,
          aggressive: true,
          content_preview: '{"test": "data"}',
        },
      ],
      total: 1,
      limit: 50,
      offset: 0,
    };

    (api.history.list as vi.Mock).mockResolvedValue(mockHistory);
    (api.history.analytics as vi.Mock).mockResolvedValue({
      total_compressions: 1,
      total_original_tokens: 100,
      total_compressed_tokens: 30,
      average_reduction_ratio: 0.7,
      by_content_type: { json: 1 },
      by_algorithm: { "json-dedup": 1 },
    });

    render(<HistoryPanel />);

    await waitFor(() => {
      expect(screen.getByText("json")).toBeInTheDocument();
      expect(screen.getByText("json-dedup")).toBeInTheDocument();
      expect(screen.getByText("100")).toBeInTheDocument();
      expect(screen.getByText("30")).toBeInTheDocument();
      // Find the ratio in the table specifically
      const ratioCells = screen.getAllByText("70.0%");
      expect(ratioCells.length).toBeGreaterThanOrEqual(1);
    });
  });

  it("shows analytics summary", async () => {
    (api.history.list as vi.Mock).mockResolvedValue({ items: [], total: 0, limit: 50, offset: 0 });
    (api.history.analytics as vi.Mock).mockResolvedValue({
      total_compressions: 5,
      total_original_tokens: 500,
      total_compressed_tokens: 200,
      average_reduction_ratio: 0.6,
      by_content_type: { json: 3, text: 2 },
      by_algorithm: { "json-dedup": 3, "text-smart": 2 },
    });

    render(<HistoryPanel />);

    await waitFor(() => {
      expect(screen.getByText("Total Compressions")).toBeInTheDocument();
      expect(screen.getByText("5")).toBeInTheDocument();
      expect(screen.getByText("Tokens Saved")).toBeInTheDocument();
      expect(screen.getByText("300")).toBeInTheDocument();
    });
  });

  it("filters by content type", async () => {
    (api.history.list as vi.Mock).mockResolvedValue({ items: [], total: 0, limit: 50, offset: 0 });
    (api.history.analytics as vi.Mock).mockResolvedValue({
      total_compressions: 0,
      total_original_tokens: 0,
      total_compressed_tokens: 0,
      average_reduction_ratio: 0,
      by_content_type: {},
      by_algorithm: {},
    });

    render(<HistoryPanel />);

    await waitFor(() => {
      const select = screen.getByRole("combobox");
      fireEvent.change(select, { target: { value: "json" } });
    });

    // Wait for the API to be called with the filter
    await waitFor(() => {
      expect(api.history.list).toHaveBeenCalledWith({ content_type: "json" });
    });
  });
});
