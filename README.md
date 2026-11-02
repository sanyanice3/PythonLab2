# streamstats

Потоковый анализ событий из CSV и JSONL, итог — JSON-отчёт. Только стандартная библиотека.

## Запуск

```bash
python -m streamstats analyze a.csv b.csv --format csv --output report.json
python -m streamstats analyze events.jsonl --format jsonl --skip-invalid
```

Без `--output` отчёт выводится в консоль. При ошибке в данных программа завершается с кодом `2`; с `--skip-invalid` неверные строки пропускаются и считаются в отчёте.

## Проверка

```bash
pip install -e ".[dev]"
python -m pytest
ruff check .
```