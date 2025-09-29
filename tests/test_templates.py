from datetime import date
from decimal import Decimal
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from report_generator.models import ReportSummary, Transaction
from report_generator.templates import build_html_report


def make_summary() -> ReportSummary:
    transactions = [
        Transaction(
            occurred_on=date(2024, 1, 1),
            category="Sales",
            description="Invoice #1001",
            amount=Decimal("1200.00"),
        ),
        Transaction(
            occurred_on=date(2024, 1, 2),
            category="Subscriptions",
            description="Monthly recurring",
            amount=Decimal("800.00"),
        ),
        Transaction(
            occurred_on=date(2024, 1, 3),
            category="Rent",
            description="Office lease",
            amount=Decimal("-600.00"),
        ),
    ]

    totals_by_category = {
        "Sales": Decimal("1200.00"),
        "Subscriptions": Decimal("800.00"),
        "Rent": Decimal("-600.00"),
    }

    totals_by_day = {
        date(2024, 1, 1): Decimal("1200.00"),
        date(2024, 1, 2): Decimal("800.00"),
        date(2024, 1, 3): Decimal("-600.00"),
    }

    total_amount = sum((txn.amount for txn in transactions), Decimal("0"))

    return ReportSummary(
        transactions=transactions,
        total_amount=total_amount,
        totals_by_category=totals_by_category,
        totals_by_day=totals_by_day,
    )


def test_html_report_has_hero_heading_and_kpi_section():
    summary = make_summary()

    html = build_html_report(summary)

    assert '<h1 class="hero__title">' in html
    assert 'class="kpi-grid"' in html


def test_html_report_includes_key_metric_values():
    summary = make_summary()

    html = build_html_report(summary)

    assert "Total Revenue" in html
    assert "$2,000.00" in html  # 1200 + 800 revenue
    assert "$600.00" in html  # expense total rendered as positive value
