"""Merged report generator building on prior attempts."""

from __future__ import annotations

from typing import Iterable

from .data_sources import load_transactions
from .models import ReportSummary, Transaction
from .summary import summarize_transactions
from .templates import build_html_report, build_markdown_report

__all__ = [
    "Transaction",
    "ReportSummary",
    "load_transactions",
    "summarize_transactions",
    "build_markdown_report",
    "build_html_report",
    "generate_report",
]


def generate_report(arguments: Iterable[str] | None = None) -> str:
    """Delegate to :mod:`report_generator.cli` without creating import loops."""

    from .cli import generate_report as _generate_report

    return _generate_report(arguments)
