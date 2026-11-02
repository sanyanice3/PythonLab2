import csv
import json


def parse_csv(path):
    with open(path, encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for record in reader:
            yield reader.line_num, record


def parse_jsonl(path):
    with open(path, encoding="utf-8") as file:
        for number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except ValueError:
                record = None
            yield number, record


PARSERS = {"csv": parse_csv, "jsonl": parse_jsonl}
