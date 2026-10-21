import { useState } from "react";
import type { CompressResponse } from "../types/api";

interface CompressionResultProps {
  result: CompressResponse | null;
  onCopy?: () => void;
  onDownload?: () => void;
}

export function CompressionResult({ result, onCopy, onDownload }: CompressionResultProps) {
  if (!result) return null;

  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(result.compressed);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      onCopy?.();
    } catch (e) {
      console.error("Copy failed:", e);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([result.compressed], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "compressed.json";
    a.click();
    URL.revokeObjectURL(url);
    onDownload?.();
  };

  const savings = (result.reduction_ratio * 100).toFixed(1);

  return (
    <div className="compression-result">
      <div className="result-header">
        <h3>Compressed Output</h3>
        <div className="result-stats">
          <span className="stat">
            <strong>{result.original_tokens}</strong> → <strong>{result.compressed_tokens}</strong> tokens
          </span>
          <span className="stat savings">{savings}% reduction</span>
          <span className="stat algorithm">{result.algorithm}</span>
        </div>
      </div>

      <div className="result-actions">
        <button onClick={handleCopy} className="btn btn-secondary" disabled={copied}>
          {copied ? "Copied!" : "Copy"}
        </button>
        <button onClick={handleDownload} className="btn btn-secondary">
          Download
        </button>
      </div>

      <pre className="result-content">{result.compressed}</pre>
    </div>
  );
}