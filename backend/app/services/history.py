"""History service for compression operations."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID

from app.models.schemas import (
    AnalyticsSummary,
    CompressionRecord,
    HistoryQuery,
    HistoryResponse,
)


class HistoryService:
    """Service for storing and retrieving compression history."""

    def __init__(self, db_path: str = "compression_history.db") -> None:
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database schema."""
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS compression_history (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    algorithm TEXT NOT NULL,
                    original_tokens INTEGER NOT NULL,
                    compressed_tokens INTEGER NOT NULL,
                    reduction_ratio REAL NOT NULL,
                    aggressive INTEGER NOT NULL,
                    content_preview TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_history_timestamp
                ON compression_history(timestamp DESC)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_history_content_type
                ON compression_history(content_type)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_history_algorithm
                ON compression_history(algorithm)
                """
            )

    @contextmanager
    def _conn(self):
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def record_compression(
        self,
        content_type: str,
        algorithm: str,
        original_tokens: int,
        compressed_tokens: int,
        reduction_ratio: float,
        aggressive: bool,
        content_preview: str,
    ) -> CompressionRecord:
        """Record a compression operation."""
        record = CompressionRecord(
            content_type=content_type,
            algorithm=algorithm,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            reduction_ratio=reduction_ratio,
            aggressive=aggressive,
            content_preview=content_preview[:200],
        )
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO compression_history
                (id, timestamp, content_type, algorithm, original_tokens,
                 compressed_tokens, reduction_ratio, aggressive, content_preview)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(record.id),
                    record.timestamp.isoformat(),
                    record.content_type,
                    record.algorithm,
                    record.original_tokens,
                    record.compressed_tokens,
                    record.reduction_ratio,
                    int(record.aggressive),
                    record.content_preview,
                ),
            )
        return record

    def get_history(self, query: HistoryQuery) -> HistoryResponse:
        """Retrieve compression history with filtering and pagination."""
        conditions = []
        params: list = []

        if query.content_type:
            conditions.append("content_type = ?")
            params.append(query.content_type)
        if query.algorithm:
            conditions.append("algorithm = ?")
            params.append(query.algorithm)
        if query.min_ratio is not None:
            conditions.append("reduction_ratio >= ?")
            params.append(query.min_ratio)
        if query.since:
            conditions.append("timestamp >= ?")
            params.append(query.since.isoformat())
        if query.until:
            conditions.append("timestamp <= ?")
            params.append(query.until.isoformat())

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

        with self._conn() as conn:
            # Get total count
            total = conn.execute(
                f"SELECT COUNT(*) FROM compression_history{where_clause}",
                params,
            ).fetchone()[0]

            # Get paginated items
            params.extend([query.limit, query.offset])
            rows = conn.execute(
                f"""
                SELECT * FROM compression_history{where_clause}
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
                """,
                params,
            ).fetchall()

        items = [
            CompressionRecord(
                id=UUID(row["id"]),
                timestamp=datetime.fromisoformat(row["timestamp"]),
                content_type=row["content_type"],
                algorithm=row["algorithm"],
                original_tokens=row["original_tokens"],
                compressed_tokens=row["compressed_tokens"],
                reduction_ratio=row["reduction_ratio"],
                aggressive=bool(row["aggressive"]),
                content_preview=row["content_preview"],
            )
            for row in rows
        ]

        return HistoryResponse(
            items=items,
            total=total,
            limit=query.limit,
            offset=query.offset,
        )

    def get_analytics(self) -> AnalyticsSummary:
        """Get aggregated compression analytics."""
        with self._conn() as conn:
            row = conn.execute(
                """
                SELECT
                    COUNT(*) as total,
                    SUM(original_tokens) as total_original,
                    SUM(compressed_tokens) as total_compressed,
                    AVG(reduction_ratio) as avg_ratio
                FROM compression_history
                """
            ).fetchone()

            total = row["total"] or 0
            total_original = row["total_original"] or 0
            total_compressed = row["total_compressed"] or 0
            avg_ratio = row["avg_ratio"] or 0.0

            # By content type
            by_content_type = dict(
                conn.execute(
                    """
                    SELECT content_type, COUNT(*)
                    FROM compression_history
                    GROUP BY content_type
                    """
                ).fetchall()
            )

            # By algorithm
            by_algorithm = dict(
                conn.execute(
                    """
                    SELECT algorithm, COUNT(*)
                    FROM compression_history
                    GROUP BY algorithm
                    """
                ).fetchall()
            )

        return AnalyticsSummary(
            total_compressions=total,
            total_original_tokens=total_original,
            total_compressed_tokens=total_compressed,
            average_reduction_ratio=round(avg_ratio, 4),
            by_content_type=by_content_type,
            by_algorithm=by_algorithm,
        )

    def clear_history(self) -> int:
        """Clear all history records. Returns count of deleted records."""
        with self._conn() as conn:
            cursor = conn.execute("DELETE FROM compression_history")
            return cursor.rowcount


# Singleton instance
history_service = HistoryService()

