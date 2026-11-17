"""Validation and normalisation of raw records."""
from __future__ import annotations

import re
from typing import Any

from etl.errors import ValidationError

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
VALID_STATUSES = {"PENDING", "SHIPPED", "DELIVERED", "CANCELLED"}


def _to_number(value: Any) -> float | None:
    """Parse '1,150' / ' 4 ' / 185 into a number; None if not numeric."""
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


class DataTransformer:
    """Validates and normalises records. Keeps the rejected ones and why."""

    def __init__(self, required_fields: list[str]) -> None:
        self.required_fields = required_fields
        self.rejected: list[ValidationError] = []
        self._seen_ids: set[str] = set()

    def validate(self, record: dict[str, Any]) -> list[str]:
        """Return the reasons this record is invalid (empty list means valid)."""
        reasons = [
            f"missing {name}"
            for name in self.required_fields
            if not str(record.get(name) or "").strip()
        ]

        email = str(record.get("customer_email") or "").strip()
        if email and not EMAIL_RE.match(email):
            reasons.append(f"invalid email {email!r}")

        if "quantity" in record:
            qty = _to_number(record["quantity"])
            if qty is None:
                reasons.append(f"quantity not numeric {record['quantity']!r}")
            elif qty <= 0 or not qty.is_integer():
                reasons.append(f"quantity must be a positive whole number, got {record['quantity']!r}")

        if "unit_price_kes" in record:
            price = _to_number(record["unit_price_kes"])
            if price is None:
                reasons.append(f"unit_price_kes not numeric {record['unit_price_kes']!r}")
            elif price <= 0:
                reasons.append(f"unit_price_kes must be positive, got {record['unit_price_kes']!r}")

        status = str(record.get("status") or "").strip().upper()
        if status and status not in VALID_STATUSES:
            reasons.append(f"unknown status {status!r}")

        order_id = str(record.get("order_id") or "").strip()
        if order_id and order_id in self._seen_ids:
            reasons.append(f"duplicate order_id {order_id}")

        return reasons

    def clean(self, record: dict[str, Any]) -> dict[str, Any]:
        """Return a normalised copy of a valid record."""
        cleaned = {k: v.strip() if isinstance(v, str) else v for k, v in record.items()}
        if "city" in cleaned:
            cleaned["city"] = cleaned["city"].title()
        if "customer_email" in cleaned:
            cleaned["customer_email"] = cleaned["customer_email"].lower()
        if "status" in cleaned:
            cleaned["status"] = cleaned["status"].upper()
        if "quantity" in cleaned:
            cleaned["quantity"] = int(_to_number(cleaned["quantity"]))
        if "unit_price_kes" in cleaned:
            cleaned["unit_price_kes"] = _to_number(cleaned["unit_price_kes"])
            if "quantity" in cleaned:
                cleaned["total_kes"] = cleaned["quantity"] * cleaned["unit_price_kes"]
        return cleaned

    def transform(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        self.rejected = []
        self._seen_ids = set()
        valid: list[dict[str, Any]] = []
        for index, record in enumerate(records, start=1):
            reasons = self.validate(record)
            order_id = str(record.get("order_id") or "").strip()
            if reasons:
                self.rejected.append(ValidationError(order_id or f"row {index}", reasons))
                continue
            if order_id:
                self._seen_ids.add(order_id)
            valid.append(self.clean(record))
        return valid
