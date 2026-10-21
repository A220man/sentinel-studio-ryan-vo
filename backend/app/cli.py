"""CLI entrypoint for Sentinel Studio compression."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.core.compression import compress_auto, compress_json, compress_text, decompress_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sentinel",
        description="Compress tool outputs, logs, files, and RAG chunks before they reach the LLM",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # compress command
    compress_parser = subparsers.add_parser("compress", help="Compress input data")
    compress_parser.add_argument("input", nargs="?", help="Input file (stdin if omitted)")
    compress_parser.add_argument("-o", "--output", help="Output file (stdout if omitted)")
    compress_parser.add_argument(
        "--type",
        choices=["auto", "json", "text"],
        default="auto",
        help="Input type detection (default: auto)",
    )
    compress_parser.add_argument(
        "--no-aggressive",
        action="store_true",
        help="Disable aggressive JSON deduplication",
    )
    compress_parser.add_argument(
        "--show-stats",
        action="store_true",
        help="Show compression statistics to stderr",
    )

    # decompress command
    decompress_parser = subparsers.add_parser("decompress", help="Decompress JSON data")
    decompress_parser.add_argument("input", nargs="?", help="Input file (stdin if omitted)")
    decompress_parser.add_argument("-o", "--output", help="Output file (stdout if omitted)")

    return parser


def read_input(path: str | None) -> str:
    if path is None or path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def write_output(data: str, path: str | None) -> None:
    if path is None or path == "-":
        sys.stdout.write(data)
    else:
        Path(path).write_text(data, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "compress":
        data = read_input(args.input)
        aggressive = not args.no_aggressive

        if args.type == "json":
            result = compress_json(data, aggressive=aggressive)
        elif args.type == "text":
            result = compress_text(data)
        else:
            result = compress_auto(data, aggressive=aggressive)

        write_output(result.compressed, args.output)

        if args.show_stats:
            sys.stderr.write(
                f"Original tokens: {result.original_tokens}\n"
                f"Compressed tokens: {result.compressed_tokens}\n"
                f"Reduction: {result.ratio:.1%}\n"
                f"Algorithm: {result.algorithm}\n"
            )

    elif args.command == "decompress":
        data = read_input(args.input)
        result = decompress_json(data)
        write_output(result, args.output)

    return 0


if __name__ == "__main__":
    sys.exit(main())