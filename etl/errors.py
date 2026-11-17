"""Custom exceptions raised by the ETL framework."""


class ETLError(Exception):
    """Base class for errors raised by the framework."""


class ExtractionError(ETLError):
    """Raised when a source cannot be read."""


class ValidationError(ETLError):
    """Raised (or collected) when a record fails validation."""

    def __init__(self, record_id: str, reasons: list[str]) -> None:
        self.record_id = record_id
        self.reasons = reasons
        super().__init__(f"{record_id}: {'; '.join(reasons)}")


class LoadError(ETLError):
    """Raised when records cannot be written to the destination."""
