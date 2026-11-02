import json


def build_report(stats):
    return {
        "total": stats.total,
        "skipped": stats.skipped,
        "levels": dict(stats.levels),
        "sources": dict(stats.sources),
        "top_error_sources": [
            {"source": source, "count": count} for source, count in stats.top_errors()
        ],
        "first_timestamp": stats.first.isoformat() if stats.first else None,
        "last_timestamp": stats.last.isoformat() if stats.last else None,
    }


def report_text(stats):
    return json.dumps(build_report(stats), ensure_ascii=False, indent=2)
