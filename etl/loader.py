"""Writes transformed records to disk."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from etl.errors import LoadError


class DataLoader:
    """Writes transformed records to a destination file (CSV or JSON by extension)."""

    SUPPORTED = {".csv", ".json"}

    def __init__(self, destination: Path) -> None:
        self.destination = Path(destination)
        if self.destination.suffix.lower() not in self.SUPPORTED:
            raise LoadError(
                f"Unsupported destination {self.destination.name!r}; use one of {sorted(self.SUPPORTED)}"
            )

    def load(self, records: list[dict[str, Any]]) -> int:
        """Write the records and return how many were written."""
        try:
            self.destination.parent.mkdir(parents=True, exist_ok=True)
            if self.destination.suffix.lower() == ".json":
                self._write_json(records)
            else:
                self._write_csv(records)
        except OSError as exc:
            raise LoadError(f"Could not write {self.destination}: {exc}") from exc
        return len(records)

    def _write_json(self, records: list[dict[str, Any]]) -> None:
        with self.destination.open("w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

    def _write_csv(self, records: list[dict[str, Any]]) -> None:
        # Union of keys, in first-seen order, so no column is dropped.
        fieldnames = list(dict.fromkeys(k for r in records for k in r))
        with self.destination.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

    def __repr__(self) -> str:
        return f"DataLoader(destination={str(self.destination)!r})"
