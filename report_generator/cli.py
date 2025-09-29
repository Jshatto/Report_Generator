"""Command line entry point combining the previous attempts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from .data_sources import load_transactions
from .summary import summarize_transactions
from .templates import build_html_report, build_markdown_report


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate financial reports")
    parser.add_argument(
        "input",
        type=Path,
        help="Path to a JSON or CSV file containing transaction data",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Destination file. If omitted the report is printed to stdout.",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=("markdown", "html", "json"),
        default="markdown",
        help="Output format for the generated report",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print JSON output",
    )
    return parser


def generate_report(arguments: Iterable[str] | None = None) -> str:
    parser = build_argument_parser()
    args = parser.parse_args(arguments)

    transactions = load_transactions(args.input)
    summary = summarize_transactions(transactions)

    match args.format:
        case "markdown":
            rendered = build_markdown_report(summary)
        case "html":
            rendered = build_html_report(summary)
        case "json":
            rendered = json.dumps(summary.as_dict(), indent=2 if args.pretty else None)
        case _ as unreachable:  # pragma: no cover - safeguarded by argparse
            raise ValueError(unreachable)

    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
        return str(args.output)

    print(rendered)
    return ""


def main() -> None:  # pragma: no cover - thin wrapper
    generate_report()


if __name__ == "__main__":  # pragma: no cover
    main()
