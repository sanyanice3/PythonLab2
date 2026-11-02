from dataclasses import dataclass
from datetime import datetime, timezone

from .errors import InvalidEventError, InvalidTimestampError

LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


@dataclass
class Event:
    timestamp: datetime
    level: str
    source: str
    message: str


def parse_timestamp(text):
    try:
        value = datetime.fromisoformat(text)
    except ValueError:
        raise InvalidTimestampError(f"неверная временная метка: {text!r}") from None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value


def make_event(record):
    if not isinstance(record, dict):
        raise InvalidEventError("запись не является объектом")
    for name in ("timestamp", "level", "source", "message"):
        if not isinstance(record.get(name), str):
            raise InvalidEventError(f"поле {name} отсутствует или не строка")
    if record["level"] not in LEVELS:
        raise InvalidEventError(f"неверный уровень: {record['level']!r}")
    if not record["source"].strip():
        raise InvalidEventError("пустой source")
    return Event(
        parse_timestamp(record["timestamp"]),
        record["level"],
        record["source"],
        record["message"],
    )
