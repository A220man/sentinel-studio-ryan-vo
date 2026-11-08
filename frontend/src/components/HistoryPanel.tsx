import { useState, useEffect, useCallback } from "react";
import { api } from "../api/client";
import type { HistoryResponse, CompressionRecord, AnalyticsSummary, HistoryQueryParams } from "../types/api";
import "./HistoryPanel.css";

export function HistoryPanel() {
  const [history, setHistory] = useState<HistoryResponse | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [contentTypeFilter, setContentTypeFilter] = useState<string>("");
  const [algorithmFilter, setAlgorithmFilter] = useState<string>("");
  const [minRatioFilter, setMinRatioFilter] = useState<string>("");
  const [sinceFilter, setSinceFilter] = useState<string>("");
  const [untilFilter, setUntilFilter] = useState<string>("");
  const [page, setPage] = useState(0);
  const PAGE_SIZE = 50;

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params: HistoryQueryParams = {
        limit: PAGE_SIZE,
        offset: page * PAGE_SIZE,
        content_type: contentTypeFilter || undefined,
        algorithm: algorithmFilter || undefined,
        min_ratio: minRatioFilter ? parseFloat(minRatioFilter) : undefined,
        since: sinceFilter || undefined,
        until: untilFilter || undefined,
      };
      const response = await api.history.list(params);
      setHistory(response);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load history");
    } finally {
      setLoading(false);
    }
  }, [contentTypeFilter, algorithmFilter, minRatioFilter, sinceFilter, untilFilter, page]);

  const fetchAnalytics = useCallback(async () => {
    try {
      const response = await api.history.analytics();
      setAnalytics(response);
    } catch (e) {
      // Analytics failure is non-critical
      console.warn("Failed to load analytics:", e);
    }
  }, []);

  const handleClear = async () => {
    if (!confirm("Clear all compression history?")) return;
    try {
      await api.history.clear();
      fetchHistory();
      fetchAnalytics();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to clear history");
    }
  };

  const handlePageChange = (newPage: number) => {
    if (newPage >= 0 && history && newPage * PAGE_SIZE < history.total) {
      setPage(newPage);
    }
  };

  useEffect(() => {
    fetchHistory();
    fetchAnalytics();
  }, [fetchHistory, fetchAnalytics]);

  useEffect(() => {
    setPage(0);
  }, [contentTypeFilter, algorithmFilter, minRatioFilter, sinceFilter, untilFilter]);

  const formatDate = (iso: string) => {
    const date = new Date(iso);
    return date.toLocaleString();
  };

  const formatRatio = (ratio: number) => {
    return `${(ratio * 100).toFixed(1)}%`;
  };

  return (
    <div className="history-panel">
      <div className="panel-header">
        <h2>Compression History</h2>
        <div className="header-actions">
          <select
            value={contentTypeFilter}
            onChange={(e) => setContentTypeFilter(e.target.value)}
            className="filter-select"
            aria-label="Filter by content type"
          >
            <option value="">All Types</option>
            <option value="json">JSON</option>
            <option value="text">Text/Code</option>
            <option value="auto">Auto-detected</option>
          </select>
          <select
            value={algorithmFilter}
            onChange={(e) => setAlgorithmFilter(e.target.value)}
            className="filter-select"
            aria-label="Filter by algorithm"
          >
            <option value="">All Algorithms</option>
            <option value="json-dedup">JSON Deduplication</option>
            <option value="json-fallback">JSON Fallback</option>
            <option value="text-smart">Text Smart</option>
            <option value="text-fallback">Text Fallback</option>
          </select>
          <input
            type="number"
            step="0.01"
            min="0"
            max="1"
            placeholder="Min reduction (0-1)"
            value={minRatioFilter}
            onChange={(e) => setMinRatioFilter(e.target.value)}
            className="filter-input"
          />
          <input
            type="datetime-local"
            value={sinceFilter}
            onChange={(e) => setSinceFilter(e.target.value)}
            className="filter-input"
            title="Since (inclusive)"
          />
          <input
            type="datetime-local"
            value={untilFilter}
            onChange={(e) => setUntilFilter(e.target.value)}
            className="filter-input"
            title="Until (inclusive)"
          />
          <button onClick={handleClear} className="btn btn-danger" disabled={loading}>
            Clear History
          </button>
        </div>
      </div>

      {analytics && (
        <div className="analytics-summary">
          <div className="stat">
            <span className="stat-label">Total Compressions</span>
            <span className="stat-value">{analytics.total_compressions}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Tokens Saved</span>
            <span className="stat-value">
              {analytics.total_original_tokens - analytics.total_compressed_tokens}
            </span>
          </div>
          <div className="stat">
            <span className="stat-label">Avg Reduction</span>
            <span className="stat-value">{formatRatio(analytics.average_reduction_ratio)}</span>
          </div>
        </div>
      )}

      <div className="panel-content">
        {loading && <div className="loading">Loading history...</div>}

        {error && <div className="error">{error}</div>}

        {history && history.total === 0 && !loading && (
          <div className="empty">No compression history yet. Compress something to see it here.</div>
        )}

        {history && history.items.length > 0 && (
          <div className="table-wrapper">
            <table className="history-table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Type</th>
                  <th>Algorithm</th>
                  <th>Original</th>
                  <th>Compressed</th>
                  <th>Reduction</th>
                  <th>Preview</th>
                </tr>
              </thead>
              <tbody>
                {history.items.map((record: CompressionRecord) => (
                  <tr key={record.id}>
                    <td className="time-col">{formatDate(record.timestamp)}</td>
                    <td>
                      <span className={`badge badge-${record.content_type}`}>
                        {record.content_type}
                      </span>
                    </td>
                    <td>{record.algorithm}</td>
                    <td className="tokens-col">{record.original_tokens}</td>
                    <td className="tokens-col">{record.compressed_tokens}</td>
                    <td className="ratio-col positive">{formatRatio(record.reduction_ratio)}</td>
                    <td className="preview-col" title={record.content_preview}>
                      {record.content_preview || "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {history && history.total > history.items.length && (
          <div className="pagination">
            <span>
              Showing {page * PAGE_SIZE + 1}-{Math.min((page + 1) * PAGE_SIZE, history.total)} of {history.total}
            </span>
            <div className="pagination-controls">
              <button
                onClick={() => handlePageChange(page - 1)}
                disabled={page === 0}
                className="btn btn-secondary"
              >
                Previous
              </button>
              <button
                onClick={() => handlePageChange(page + 1)}
                disabled={(page + 1) * PAGE_SIZE >= history.total}
                className="btn btn-secondary"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
