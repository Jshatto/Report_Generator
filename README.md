# Report Generator

This project merges the functionality explored in two previous prototypes
(`Attempt_1` and `Attempt_2`) into a single, reusable Python package. The final
implementation supports loading financial transactions from JSON or CSV files,
calculating useful summaries, and rendering the result as Markdown, HTML, or
JSON for downstream tooling.

## Installation

No external dependencies are required. The package only uses Python's standard
library, so it can be executed with any recent Python 3.11+ interpreter.

Clone the repository and install it in editable mode if desired:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

A sample dataset is provided in `data/sample_transactions.json`. Generate a
report via the unified command-line interface:

```bash
python -m report_generator.cli data/sample_transactions.json --format html --output report.html
```

Use `--format markdown` (default) or `--format json` for alternative outputs.
When the `--output` flag is omitted the report is written to standard output.

The original attempt scripts remain available:

- `Attempt_1/report_generator_attempt1.py` – produces Markdown output.
- `Attempt_2/report_generator_attempt2.py` – produces HTML output.

Both now delegate to the shared `report_generator` package so that bug fixes and
feature additions apply consistently.
