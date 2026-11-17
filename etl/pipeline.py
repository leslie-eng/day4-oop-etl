"""Wires extractor -> transformer -> loader together."""
from __future__ import annotations

from dataclasses import dataclass, field

from etl.errors import ETLError
from etl.extractors import DataExtractor
from etl.loader import DataLoader
from etl.transformer import DataTransformer


@dataclass
class RunSummary:
    """Collects the numbers printed at the end of a pipeline run."""

    source: str
    extracted: int = 0
    valid: int = 0
    rejected: int = 0
    loaded: int = 0
    errors: list[str] = field(default_factory=list)

    def report(self) -> str:
        lines = [
            f"Pipeline run: {self.source}",
            f"  extracted : {self.extracted}",
            f"  valid     : {self.valid}",
            f"  rejected  : {self.rejected}",
            f"  loaded    : {self.loaded}",
        ]
        if self.errors:
            lines.append(f"  errors ({len(self.errors)}):")
            lines.extend(f"    - {e}" for e in self.errors)
        return "\n".join(lines)


class Pipeline:
    """Runs extractor -> transformer -> loader. Must not care which extractor it was given."""

    def __init__(self, extractor: DataExtractor, transformer: DataTransformer, loader: DataLoader) -> None:
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader

    def run(self) -> RunSummary:
        summary = RunSummary(source=self.extractor.name)
        try:
            raw = self.extractor.extract()
            summary.extracted = len(raw)

            valid = self.transformer.transform(raw)
            summary.valid = len(valid)
            summary.rejected = len(self.transformer.rejected)
            summary.errors.extend(str(e) for e in self.transformer.rejected)

            summary.loaded = self.loader.load(valid)
        except ETLError as exc:
            # A failed stage ends the run but still produces a summary.
            summary.errors.append(f"{type(exc).__name__}: {exc}")
        return summary
