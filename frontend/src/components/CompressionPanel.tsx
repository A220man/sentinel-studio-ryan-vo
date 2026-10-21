import { useState } from "react";
import { api } from "../api/client";
import type { CompressRequest, CompressResponse } from "../types/api";
import { CompressionResult } from "./CompressionResult";
import "./CompressionPanel.css";

export function CompressionPanel() {
  const [input, setInput] = useState("");
  const [contentType, setContentType] = useState<"auto" | "json" | "text">("auto");
  const [aggressive, setAggressive] = useState(true);
  const [result, setResult] = useState<CompressResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCompress = async () => {
    if (!input.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const request: CompressRequest = {
        content: input,
        content_type: contentType,
        aggressive,
      };
      const response = await api.compress.single(request);
      setResult(response);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Compression failed");
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setInput("");
    setResult(null);
    setError(null);
  };

  return (
    <div className="compression-panel">
      <div className="panel-header">
        <h2>Sentinel Studio</h2>
        <p className="subtitle">Compress tool outputs, logs, files, and RAG chunks for LLM token efficiency</p>
      </div>

      <div className="panel-content">
        <div className="input-section">
          <div className="input-controls">
            <label>
              <select value={contentType} onChange={(e) => setContentType(e.target.value as "auto" | "json" | "text")}>
                <option value="auto">Auto-detect</option>
                <option value="json">JSON (60-95% reduction)</option>
                <option value="text">Text/Code (~20% reduction)</option>
              </select>
              <span>Content Type</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={aggressive}
                onChange={(e) => setAggressive(e.target.checked)}
              />
              <span>Aggressive JSON deduplication</span>
            </label>
          </div>

          <textarea
            className="input-textarea"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Paste JSON, logs, code, or RAG chunks here..."
            rows={15}
            spellCheck={false}
          />

          <div className="input-actions">
            <button
              className="btn btn-primary"
              onClick={handleCompress}
              disabled={loading || !input.trim()}
            >
              {loading ? "Compressing..." : "Compress"}
            </button>
            <button className="btn btn-secondary" onClick={handleClear} disabled={!input && !result}>
              Clear
            </button>
          </div>

          {error && <div className="error-message">{error}</div>}
        </div>

        <CompressionResult result={result} />
      </div>

      <footer className="panel-footer">
        <p>
          Built for AI/ML developers | <a href="https://github.com/headroomlabs-ai/headroom" target="_blank" rel="noopener">Reference: headroom</a>
        </p>
      </footer>
    </div>
  );
}