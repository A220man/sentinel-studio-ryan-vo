"""Tests for CLI entrypoint."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Get the backend directory (parent of tests/)
BACKEND_DIR = Path(__file__).parent.parent


def run_cli(*args: str, input_data: str | None = None) -> subprocess.CompletedProcess[str]:
    """Run CLI command from backend directory."""
    return subprocess.run(
        [sys.executable, "-m", "app.cli", *args],
        input=input_data,
        capture_output=True,
        text=True,
        cwd=BACKEND_DIR,
    )


def test_cli_compress_stdin_stdout() -> None:
    """Test CLI compress with stdin/stdout."""
    proc = run_cli("compress", input_data='{"test": "value", "test": "value"}')
    assert proc.returncode == 0
    assert "§" in proc.stdout or "test" in proc.stdout


def test_cli_compress_file() -> None:
    """Test CLI compress with file input."""
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('{"items": [{"name": "repeat"}, {"name": "repeat"}]}')
        temp_path = f.name

    try:
        proc = run_cli("compress", temp_path)
        assert proc.returncode == 0
        assert len(proc.stdout) > 0
    finally:
        os.unlink(temp_path)


def test_cli_compress_show_stats() -> None:
    """Test CLI compress with --show-stats."""
    proc = run_cli("compress", "--show-stats", input_data='{"data": "test"}')
    assert proc.returncode == 0
    assert "Original tokens:" in proc.stderr
    assert "Compressed tokens:" in proc.stderr
    assert "Reduction:" in proc.stderr


def test_cli_decompress() -> None:
    """Test CLI decompress."""
    # First compress something
    compress_proc = run_cli("compress", input_data='{"items": [{"name": "repeat"}, {"name": "repeat"}]}')
    assert compress_proc.returncode == 0
    compressed = compress_proc.stdout

    # Then decompress
    decompress_proc = run_cli("decompress", input_data=compressed)
    assert decompress_proc.returncode == 0
    # Should restore original structure
    assert "repeat" in decompress_proc.stdout
    assert "items" in decompress_proc.stdout


def test_cli_help() -> None:
    """Test CLI help output."""
    proc = run_cli("--help")
    assert proc.returncode == 0
    assert "sentinel" in proc.stdout
    assert "compress" in proc.stdout
    assert "decompress" in proc.stdout