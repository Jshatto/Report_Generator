"""Data models used across the report generator package."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable, Mapping


@dataclass(frozen=True, slots=True)
class Transaction:
    """Represents a single financial transaction."""

    occurred_on: date
    category: str
    description: str
    amount: Decimal

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> "Transaction":
        """Create a :class:`Transaction` from a mapping of basic Python types.

        Parameters
        ----------
        data:
            A mapping that must contain the keys ``date``, ``category``,
            ``description`` and ``amount``. The ``date`` value can either be a
            :class:`datetime.date` or an ISO formatted string (``YYYY-MM-DD``).

        Returns
        -------
        Transaction
            A populated dataclass ready to be used throughout the report
            generator.
        """

        raw_date = data["date"]
        if isinstance(raw_date, date):
            occurred_on = raw_date
        elif isinstance(raw_date, str):
            occurred_on = date.fromisoformat(raw_date)
        else:
            msg = "Unsupported date value in transaction mapping"
            raise TypeError(msg)

        amount = data["amount"]
        if isinstance(amount, Decimal):
            amount_value = amount
        elif isinstance(amount, (int, float, str)):
            amount_value = Decimal(str(amount))
        else:
            msg = "Unsupported amount value in transaction mapping"
            raise TypeError(msg)

        return cls(
            occurred_on=occurred_on,
            category=str(data["category"]),
            description=str(data["description"]),
            amount=amount_value,
        )


@dataclass(slots=True)
class ReportSummary:
    """A lightweight container for all derived report information."""

    transactions: list[Transaction]
    total_amount: Decimal
    totals_by_category: dict[str, Decimal]
    totals_by_day: dict[date, Decimal]

    def as_dict(self) -> dict[str, object]:
        """Return a JSON serialisable representation of the summary."""

        return {
            "transactions": [
                {
                    "date": transaction.occurred_on.isoformat(),
                    "category": transaction.category,
                    "description": transaction.description,
                    "amount": str(transaction.amount),
                }
                for transaction in self.transactions
            ],
            "total_amount": str(self.total_amount),
            "totals_by_category": {
                category: str(total)
                for category, total in sorted(self.totals_by_category.items())
            },
            "totals_by_day": {
                day.isoformat(): str(total)
                for day, total in sorted(self.totals_by_day.items())
            },
        }

    def __bool__(self) -> bool:  # pragma: no cover - convenience method
        return bool(self.transactions)


IterableTransactions = Iterable[Transaction]
