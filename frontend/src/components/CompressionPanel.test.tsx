import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { CompressionPanel } from "./CompressionPanel";

// Mock the API client before importing
vi.mock("../api/client", () => ({
  api: {
    compress: {
      single: vi.fn(),
      batch: vi.fn(),
    },
  },
}));

import { api } from "../api/client";

describe("CompressionPanel", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the panel with title and subtitle", () => {
    render(<CompressionPanel />);
    expect(screen.getByText("Sentinel Studio")).toBeInTheDocument();
    expect(screen.getByText(/Compress tool outputs/i)).toBeInTheDocument();
  });

  it("has textarea for input", () => {
    render(<CompressionPanel />);
    const textarea = screen.getByPlaceholderText(/Paste JSON, logs, code, or RAG chunks here/i);
    expect(textarea).toBeInTheDocument();
  });

  it("has content type selector", () => {
    render(<CompressionPanel />);
    const select = screen.getByRole("combobox");
    expect(select).toBeInTheDocument();
    expect(select).toHaveValue("auto");
  });

  it("has aggressive checkbox", () => {
    render(<CompressionPanel />);
    const checkbox = screen.getByLabelText(/Aggressive JSON deduplication/i);
    expect(checkbox).toBeInTheDocument();
    expect(checkbox).toBeChecked();
  });

  it("compress button is disabled when input is empty", () => {
    render(<CompressionPanel />);
    const button = screen.getByRole("button", { name: /Compress/i });
    expect(button).toBeDisabled();
  });

  it("enables compress button when input is provided", () => {
    render(<CompressionPanel />);
    const textarea = screen.getByPlaceholderText(/Paste JSON, logs, code, or RAG chunks here/i);
    fireEvent.change(textarea, { target: { value: '{"test": "value"}' } });
    const button = screen.getByRole("button", { name: /Compress/i });
    expect(button).not.toBeDisabled();
  });

  it("calls API on compress and displays result", async () => {
    const mockResponse = {
      compressed: '{"test":"value"}',
      original_tokens: 10,
      compressed_tokens: 5,
      reduction_ratio: 0.5,
      algorithm: "json-dedup",
    };
    vi.mocked(api.compress.single).mockResolvedValue(mockResponse);

    render(<CompressionPanel />);
    const textarea = screen.getByPlaceholderText(/Paste JSON, logs, code, or RAG chunks here/i);
    const button = screen.getByRole("button", { name: /Compress/i });

    fireEvent.change(textarea, { target: { value: '{"test": "value"}' } });
    await userEvent.click(button);

    await waitFor(() => {
      expect(api.compress.single).toHaveBeenCalledWith({
        content: '{"test": "value"}',
        content_type: "auto",
        aggressive: true,
      });
    });

    await waitFor(() => {
      expect(screen.getByText("Compressed Output")).toBeInTheDocument();
      expect(screen.getByText("50.0% reduction")).toBeInTheDocument();
      expect(screen.getByText("json-dedup")).toBeInTheDocument();
    });
  });

  it("displays error message on API failure", async () => {
    vi.mocked(api.compress.single).mockRejectedValue(new Error("Network error"));

    render(<CompressionPanel />);
    const textarea = screen.getByPlaceholderText(/Paste JSON, logs, code, or RAG chunks here/i);
    const button = screen.getByRole("button", { name: /Compress/i });

    fireEvent.change(textarea, { target: { value: '{"test": "value"}' } });
    await userEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText("Network error")).toBeInTheDocument();
    });
  });

  it("clear button clears input and result", async () => {
    const mockResponse = {
      compressed: '{"test":"value"}',
      original_tokens: 10,
      compressed_tokens: 5,
      reduction_ratio: 0.5,
      algorithm: "json-dedup",
    };
    vi.mocked(api.compress.single).mockResolvedValue(mockResponse);

    render(<CompressionPanel />);
    const textarea = screen.getByPlaceholderText(/Paste JSON, logs, code, or RAG chunks here/i);
    const compressBtn = screen.getByRole("button", { name: /Compress/i });

    fireEvent.change(textarea, { target: { value: '{"test": "value"}' } });
    await userEvent.click(compressBtn);

    await waitFor(() => {
      expect(screen.getByText("Compressed Output")).toBeInTheDocument();
    });

    const clearBtn = screen.getByRole("button", { name: /Clear/i });
    await userEvent.click(clearBtn);

    expect(textarea).toHaveValue("");
    expect(screen.queryByText("Compressed Output")).not.toBeInTheDocument();
  });
});