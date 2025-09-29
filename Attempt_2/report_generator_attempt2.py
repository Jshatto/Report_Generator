"""Legacy attempt focused on HTML output."""

from __future__ import annotations

from pathlib import Path

from report_generator import build_html_report, load_transactions, summarize_transactions


def generate_html_report(input_path: str | Path, output_path: str | Path) -> Path:
    """Generate an HTML report using the Attempt 2 workflow."""

    input_path = Path(input_path)
    output_path = Path(output_path)

    transactions = load_transactions(input_path)
    summary = summarize_transactions(transactions)
    html = build_html_report(summary)

    output_path.write_text(html, encoding="utf-8")
    return output_path
