import { useState, useEffect } from "react";
import { api } from "../api/client";
import type { HistoryResponse, CompressionRecord, AnalyticsSummary } from "../types/api";
import "./HistoryPanel.css";

export function HistoryPanel() {
  const [history, setHistory] = useState<HistoryResponse | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [contentTypeFilter, setContentTypeFilter] = useState<string>("");

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.history.list({ content_type: contentTypeFilter || undefined });
      setHistory(response);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load history");
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await api.history.analytics();
      setAnalytics(response);
    } catch (e) {
      // Analytics failure is non-critical
      console.warn("Failed to load analytics:", e);
    }
  };

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

  useEffect(() => {
    fetchHistory();
    fetchAnalytics();
  }, [contentTypeFilter]);

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
          >
            <option value="">All Types</option>
            <option value="json">JSON</option>
            <option value="text">Text/Code</option>
            <option value="auto">Auto-detected</option>
          </select>
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
        )}

        {history && history.total > history.items.length && (
          <div className="pagination">
            <span>
              Showing {history.items.length} of {history.total}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
