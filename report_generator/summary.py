"""Business logic for deriving insights from raw transactions."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Iterable

from .models import ReportSummary, Transaction


def summarize_transactions(transactions: Iterable[Transaction]) -> ReportSummary:
    """Calculate totals from the supplied transactions."""

    transactions = list(transactions)
    if not transactions:
        return ReportSummary(
            transactions=[],
            total_amount=Decimal("0"),
            totals_by_category={},
            totals_by_day={},
        )

    total_amount = sum((txn.amount for txn in transactions), Decimal("0"))

    totals_by_category: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    totals_by_day: dict[date, Decimal] = defaultdict(lambda: Decimal("0"))

    for txn in transactions:
        totals_by_category[txn.category] += txn.amount
        totals_by_day[txn.occurred_on] += txn.amount

    return ReportSummary(
        transactions=transactions,
        total_amount=total_amount,
        totals_by_category=dict(sorted(totals_by_category.items())),
        totals_by_day=dict(sorted(totals_by_day.items())),
    )
