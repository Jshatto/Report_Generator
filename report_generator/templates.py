"""Rendering helpers for human-friendly report outputs."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from textwrap import indent

from .models import ReportSummary


def build_markdown_report(summary: ReportSummary) -> str:
    """Render the report as Markdown."""

    lines = ["# Financial Summary", ""]

    if not summary.transactions:
        lines.append("No transactions supplied.")
        return "\n".join(lines)

    lines.extend(_render_overview(summary))
    lines.append("")
    lines.extend(_render_category_table(summary))
    lines.append("")
    lines.extend(_render_daily_totals(summary))
    lines.append("")
    lines.append("## Transactions")
    lines.append("")
    lines.append("| Date | Category | Description | Amount |")
    lines.append("| --- | --- | --- | ---: |")
    for txn in summary.transactions:
        lines.append(
            f"| {txn.occurred_on.isoformat()} | {txn.category} | "
            f"{txn.description} | ${txn.amount:.2f} |"
        )

    return "\n".join(lines)


def build_html_report(summary: ReportSummary) -> str:
    """Render the report as a standalone HTML string."""

    if not summary.transactions:
        body = "<p>No transactions supplied.</p>"
    else:
        body = "\n".join(
            [
                "<section>",
                indent("\n".join(_render_overview(summary, html=True)), "  "),
                "</section>",
                "<section>",
                indent(_render_category_table(summary, html=True), "  "),
                "</section>",
                "<section>",
                indent(_render_daily_totals(summary, html=True), "  "),
                "</section>",
                "<section>",
                indent(_render_transaction_table(summary), "  "),
                "</section>",
            ]
        )

    return (
        "<!DOCTYPE html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        "  <meta charset=\"utf-8\">\n"
        "  <title>Financial Summary</title>\n"
        "  <style>\n"
        "    body { font-family: sans-serif; margin: 2rem; }\n"
        "    table { border-collapse: collapse; width: 100%; margin-top: 1rem; }\n"
        "    th, td { border: 1px solid #ccc; padding: 0.5rem; text-align: left; }\n"
        "    th { background: #f3f4f6; }\n"
        "    td:last-child, th:last-child { text-align: right; }\n"
        "    section { margin-bottom: 2rem; }\n"
        "  </style>\n"
        "</head>\n"
        "<body>\n"
        "<h1>Financial Summary</h1>\n"
        f"{body}\n"
        "</body>\n"
        "</html>\n"
    )


def _render_overview(summary: ReportSummary, *, html: bool = False) -> list[str]:
    lines = ["## Overview" if not html else "<h2>Overview</h2>"]

    total = f"${summary.total_amount:.2f}"
    if html:
        lines.append(f"<p>Total amount: <strong>{total}</strong></p>")
    else:
        lines.append(f"Total amount: **{total}**")

    return lines


def _render_category_table(summary: ReportSummary, *, html: bool = False) -> list[str] | str:
    if html:
        rows = "\n".join(
            f"    <tr><td>{category}</td><td>${total:.2f}</td></tr>"
            for category, total in summary.totals_by_category.items()
        )
        return (
            "<h2>Totals by category</h2>\n"
            "<table>\n"
            "  <thead><tr><th>Category</th><th>Total</th></tr></thead>\n"
            "  <tbody>\n"
            f"{rows}\n"
            "  </tbody>\n"
            "</table>"
        )

    lines = ["## Totals by category", "", "| Category | Total |", "| --- | ---: |"]
    for category, total in summary.totals_by_category.items():
        lines.append(f"| {category} | ${total:.2f} |")
    return lines


def _render_daily_totals(summary: ReportSummary, *, html: bool = False) -> list[str] | str:
    if html:
        rows = "\n".join(
            f"    <tr><td>{day.isoformat()}</td><td>${total:.2f}</td></tr>"
            for day, total in summary.totals_by_day.items()
        )
        return (
            "<h2>Totals by day</h2>\n"
            "<table>\n"
            "  <thead><tr><th>Date</th><th>Total</th></tr></thead>\n"
            "  <tbody>\n"
            f"{rows}\n"
            "  </tbody>\n"
            "</table>"
        )

    lines = ["## Totals by day", "", "| Date | Total |", "| --- | ---: |"]
    for day, total in summary.totals_by_day.items():
        lines.append(f"| {day.isoformat()} | ${total:.2f} |")
    return lines


def _render_transaction_table(summary: ReportSummary) -> str:
    rows = "\n".join(
        "    <tr>"
        f"<td>{txn.occurred_on.isoformat()}</td>"
        f"<td>{txn.category}</td>"
        f"<td>{txn.description}</td>"
        f"<td>${txn.amount:.2f}</td>"
        "</tr>"
        for txn in summary.transactions
    )

    return (
        "<h2>Transactions</h2>\n"
        "<table>\n"
        "  <thead><tr><th>Date</th><th>Category</th><th>Description</th><th>Amount</th></tr></thead>\n"
        "  <tbody>\n"
        f"{rows}\n"
        "  </tbody>\n"
        "</table>"
    )
