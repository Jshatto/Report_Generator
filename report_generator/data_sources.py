"""Utilities for loading transaction data from disk."""

from __future__ import annotations

from csv import DictReader
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
from typing import Iterable

from .models import Transaction

SUPPORTED_EXTENSIONS = {".json", ".csv"}


def _normalise_category(value: str) -> str:
    return value.strip() or "Uncategorised"


def load_transactions(path: Path) -> list[Transaction]:
    """Load transaction data from ``path``.

    Parameters
    ----------
    path:
        A JSON or CSV file containing rows with the keys ``date``, ``category``,
        ``description`` and ``amount``.
    """

    if not path.exists():
        msg = f"No such input file: {path}"
        raise FileNotFoundError(msg)

    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        msg = f"Unsupported file type: {suffix}. Supported: {sorted(SUPPORTED_EXTENSIONS)}"
        raise ValueError(msg)

    if suffix == ".json":
        transactions = _load_json(path)
    else:
        transactions = _load_csv(path)

    return [Transaction.from_mapping(txn) for txn in transactions]


def _load_json(path: Path) -> Iterable[dict[str, object]]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, list):
        msg = "JSON input must be a list of mappings"
        raise ValueError(msg)

    for raw in payload:
        yield {
            "date": _coerce_date(raw, "date"),
            "category": _normalise_category(str(raw.get("category", ""))),
            "description": str(raw.get("description", "")),
            "amount": _coerce_amount(raw, "amount"),
        }


def _load_csv(path: Path) -> Iterable[dict[str, object]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = DictReader(handle)
        for row in reader:
            yield {
                "date": _coerce_date(row, "date"),
                "category": _normalise_category(row.get("category", "")),
                "description": row.get("description", ""),
                "amount": _coerce_amount(row, "amount"),
            }


def _coerce_date(mapping: dict[str, object], key: str) -> date:
    raw_value = mapping.get(key)
    if raw_value is None:
        msg = f"Missing '{key}' field"
        raise ValueError(msg)

    if isinstance(raw_value, date):
        return raw_value

    if isinstance(raw_value, str):
        return date.fromisoformat(raw_value.strip())

    msg = f"Unable to parse date value: {raw_value!r}"
    raise ValueError(msg)


def _coerce_amount(mapping: dict[str, object], key: str) -> Decimal:
    raw_value = mapping.get(key)
    if raw_value is None:
        msg = f"Missing '{key}' field"
        raise ValueError(msg)

    if isinstance(raw_value, Decimal):
        return raw_value

    if isinstance(raw_value, (int, float, str)):
        return Decimal(str(raw_value))

    msg = f"Unable to parse numeric value: {raw_value!r}"
    raise ValueError(msg)
