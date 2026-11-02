import json

import pytest

from streamstats.__main__ import main
from streamstats.analysis import analyze
from streamstats.errors import InvalidEventError, UnsupportedFormatError
from streamstats.parsers import parse_csv, parse_jsonl

HEADER = "timestamp,level,source,message\n"
GOOD = "2026-10-07T12:00:00+03:00,ERROR,db,сбой\n"
JSON_GOOD = {"timestamp": "2026-10-07T09:00:00+00:00", "level": "INFO", "source": "web", "message": "ok"}


def write(path, text):
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_csv_parser(tmp_path):
    path = write(tmp_path / "a.csv", HEADER + '2026-10-07T12:00:00,INFO,web,"a, b"\n')
    rows = list(parse_csv(path))
    assert rows == [(2, {"timestamp": "2026-10-07T12:00:00", "level": "INFO", "source": "web", "message": "a, b"})]


def test_jsonl_parser(tmp_path):
    path = write(tmp_path / "a.jsonl", json.dumps(JSON_GOOD) + "\n\nне json\n")
    rows = list(parse_jsonl(path))
    assert rows == [(1, JSON_GOOD), (3, None)]


def test_empty_file(tmp_path):
    stats = analyze([write(tmp_path / "a.csv", "")], "csv")
    assert stats.total == 0 and stats.first is None


def test_broken_line_stops(tmp_path):
    path = write(tmp_path / "a.jsonl", json.dumps(JSON_GOOD) + "\n{плохо\n")
    with pytest.raises(InvalidEventError, match="строка 2"):
        analyze([path], "jsonl")


def test_broken_line_skipped(tmp_path):
    path = write(tmp_path / "a.csv", HEADER + "2026-10-07T12:00:00,WRONG,web,x\n" + GOOD)
    stats = analyze([path], "csv", skip_invalid=True)
    assert stats.total == 1 and stats.skipped == 1


def test_bad_timestamp(tmp_path):
    path = write(tmp_path / "a.csv", HEADER + "вчера,INFO,web,x\n")
    with pytest.raises(Exception, match="временная метка"):
        analyze([path], "csv")


def test_unsupported_format(tmp_path):
    with pytest.raises(UnsupportedFormatError):
        analyze([], "xml")


def test_multiple_files_and_unicode(tmp_path):
    first = write(tmp_path / "a.csv", HEADER + GOOD + GOOD)
    second = write(tmp_path / "b.csv", HEADER + "2026-10-08T00:00:00+00:00,CRITICAL,кэш,x\n")
    stats = analyze([first, second], "csv")
    assert stats.total == 3
    assert stats.top_errors() == [("db", 2), ("кэш", 1)]
    assert stats.first.isoformat() == "2026-10-07T12:00:00+03:00"
    assert stats.last.isoformat() == "2026-10-08T00:00:00+00:00"


def test_cli(tmp_path, capsys):
    source = write(tmp_path / "a.csv", HEADER + GOOD)
    output = tmp_path / "report.json"
    assert main(["analyze", source, "--format", "csv", "--output", str(output)]) == 0
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["total"] == 1 and report["sources"] == {"db": 1}

    broken = write(tmp_path / "b.csv", HEADER + "x,INFO,web,m\n")
    assert main(["analyze", broken, "--format", "csv"]) == 2
    assert "b.csv, строка 2" in capsys.readouterr().err
    assert main(["analyze", broken, "--format", "csv", "--skip-invalid"]) == 0
    assert main(["analyze", "нет.csv", "--format", "csv"]) == 2
