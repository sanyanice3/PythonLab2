import logging
from collections import Counter

from .errors import InvalidEventError, InvalidTimestampError, UnsupportedFormatError
from .models import make_event
from .parsers import PARSERS

logger = logging.getLogger("streamstats")


class Stats:
    def __init__(self):
        self.total = 0
        self.skipped = 0
        self.levels = Counter()
        self.sources = Counter()
        self.error_sources = Counter()
        self.first = None
        self.last = None

    def add(self, event):
        self.total += 1
        self.levels[event.level] += 1
        self.sources[event.source] += 1
        if event.level in ("ERROR", "CRITICAL"):
            self.error_sources[event.source] += 1
        if self.first is None or event.timestamp < self.first:
            self.first = event.timestamp
        if self.last is None or event.timestamp > self.last:
            self.last = event.timestamp

    def top_errors(self, count=5):
        items = sorted(self.error_sources.items(), key=lambda item: (-item[1], item[0]))
        return items[:count]


def analyze(paths, fmt, skip_invalid=False):
    if fmt not in PARSERS:
        raise UnsupportedFormatError(f"неподдерживаемый формат: {fmt}")
    parser = PARSERS[fmt]
    stats = Stats()
    for path in paths:
        for number, record in parser(path):
            try:
                stats.add(make_event(record))
            except (InvalidEventError, InvalidTimestampError) as error:
                message = f"{path}, строка {number}: {error}"
                if not skip_invalid:
                    raise type(error)(message) from error
                logger.warning(message)
                stats.skipped += 1
    return stats
