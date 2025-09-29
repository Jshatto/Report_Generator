"""Legacy attempt focused on Markdown output."""

from __future__ import annotations

from pathlib import Path

from report_generator import build_markdown_report, load_transactions, summarize_transactions


def generate_markdown_report(input_path: str | Path, output_path: str | Path) -> Path:
    """Generate a Markdown report using the original Attempt 1 workflow."""

    input_path = Path(input_path)
    output_path = Path(output_path)

    transactions = load_transactions(input_path)
    summary = summarize_transactions(transactions)
    markdown = build_markdown_report(summary)

    output_path.write_text(markdown, encoding="utf-8")
    return output_path
