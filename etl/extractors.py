"""Data sources. Every extractor returns a list of raw dict records."""
from __future__ import annotations

import csv
import json
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from etl.errors import ExtractionError


class DataExtractor(ABC):
    """Common interface for every data source."""

    def __init__(self, source: str, name: str | None = None) -> None:
        # Store configuration only; the source is read in extract().
        self.source = str(source)
        self.name = name or self.source

    @abstractmethod
    def extract(self) -> list[dict[str, Any]]:
        """Return the raw records from the source."""

    def __repr__(self) -> str:
        return f"{type(self).__name__}(source={self.source!r}, name={self.name!r})"


class CSVExtractor(DataExtractor):
    """Reads records from a CSV file."""

    def extract(self) -> list[dict[str, Any]]:
        path = Path(self.source)
        if not path.is_file():
            raise ExtractionError(f"CSV file not found: {path}")
        try:
            with path.open(newline="", encoding="utf-8") as f:
                return list(csv.DictReader(f))
        except (OSError, UnicodeDecodeError, csv.Error) as exc:
            raise ExtractionError(f"Could not read {path}: {exc}") from exc


class APIExtractor(DataExtractor):
    """Reads records from a JSON HTTP endpoint."""

    def __init__(self, source: str, name: str | None = None, timeout: float = 10.0) -> None:
        super().__init__(source, name)
        self.timeout = timeout

    def extract(self) -> list[dict[str, Any]]:
        try:
            with urllib.request.urlopen(self.source, timeout=self.timeout) as resp:
                payload = json.load(resp)
        except (urllib.error.URLError, TimeoutError) as exc:
            raise ExtractionError(f"Request to {self.source} failed: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise ExtractionError(f"{self.source} did not return valid JSON: {exc}") from exc

        # Accept either a bare list or an envelope like {"data": [...]}.
        if isinstance(payload, dict):
            payload = next((v for v in payload.values() if isinstance(v, list)), None)
        if not isinstance(payload, list) or not all(isinstance(r, dict) for r in payload):
            raise ExtractionError(f"{self.source} did not return a list of records")
        return payload
