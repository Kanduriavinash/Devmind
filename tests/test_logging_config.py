import json
import logging

from devmind.logging_config import JsonLogFormatter


def test_json_formatter_keeps_message_and_structured_fields():
    record = logging.LogRecord("devmind", logging.INFO, "x.py", 1, "analysis done", (), None)
    record.status = "analysis_complete"
    result = json.loads(JsonLogFormatter().format(record))
    assert result["message"] == "analysis done"
    assert result["status"] == "analysis_complete"
    assert result["level"] == "INFO"
