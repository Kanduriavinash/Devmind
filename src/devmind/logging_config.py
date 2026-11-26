"""Minimal JSON logging configuration with safe, structured fields."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone


class JsonLogFormatter(logging.Formatter):
    """Format each log event as JSON with timestamp, level, and approved extras."""

    _STANDARD_FIELDS = set(logging.makeLogRecord({}).__dict__) | {"message", "asctime"}

    def format(self, record: logging.LogRecord) -> str:
        event = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in self._STANDARD_FIELDS and not key.startswith("_"):
                event[key] = value
        return json.dumps(event, ensure_ascii=False, default=str)


def configure_logging(*, verbose: bool = False) -> None:
    """Configure JSON logs to stderr."""
    handler = logging.StreamHandler()
    handler.setFormatter(JsonLogFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO if verbose else logging.WARNING)

