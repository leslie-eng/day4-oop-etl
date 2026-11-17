# Day 4 OOP ETL

A small object-oriented ETL project that cleans and validates Jumia order data from a CSV file and writes the accepted rows to a new output file.

## Overview

This repository reads the source data in `data/orders.csv`, validates each row, drops invalid records from the final output, and keeps a record of the reasons each rejected row failed validation. The pipeline then writes the valid records to `output/clean_orders.csv`.

The project is organized around a reusable ETL pattern:

- `etl/extractors.py` defines the data-source interface and a CSV extractor
- `etl/transformer.py` validates and normalizes records
- `etl/loader.py` writes CSV or JSON output
- `etl/pipeline.py` coordinates the full extract -> transform -> load flow
- `main.py` wires the pipeline to the order dataset and prints a run summary

## Features

- Reads raw order records from a CSV source
- Validates required fields such as `order_id`, `customer_email`, `quantity`, and `status`
- Checks for malformed emails, duplicate `order_id` values, non-numeric quantity, and non-positive prices
- Normalizes values such as city capitalization, lowercase email addresses, uppercase status values, and `total_kes`
- Writes only valid rows to disk
- Returns a summary of extracted, valid, rejected, and loaded records

## Workflow

The current pipeline flow is:

1. Extract records from `data/orders.csv`
2. Validate each row against the rules in `DataTransformer`
3. Reject invalid rows and collect error reasons
4. Clean valid rows and calculate `total_kes`
5. Save accepted rows to `output/clean_orders.csv`

## Project structure

```text
.
├── data/
│   └── orders.csv
├── etl/
│   ├── __init__.py
│   ├── errors.py
│   ├── extractors.py
│   ├── loader.py
│   ├── pipeline.py
│   └── transformer.py
├── output/
│   └── clean_orders.csv
├── src/
│   └── day4_oop_etl/
│       └── __init__.py
├── main.py
├── pyproject.toml
├── README.md
└── .gitignore
```

## Prerequisites

- Python 3.14+
- `uv` installed for the project environment

The repository metadata in `pyproject.toml` declares `requires-python = ">=3.14"`, and the verified working workflow in this project uses `uv`.

## Installation

```bash
git clone <repository-url>
cd day4-oop-etl
uv sync
```

## Usage

Run the ETL pipeline from the project root:

```bash
uv run python main.py
```

This executes the code in `main.py`, which reads `data/orders.csv` and writes the cleaned output to `output/clean_orders.csv`.

Example output from the current dataset:

```text
Pipeline run: orders.csv
  extracted : 25
  valid     : 19
  rejected  : 6
  loaded    : 19
```

The rejected rows are tracked by `ValidationError` messages, such as:

- missing customer email
- invalid email format
- duplicate `order_id`
- non-numeric or invalid quantity
- non-positive `unit_price_kes`

## Notes

The project also declares a console entry point in `pyproject.toml`, but the repository’s checked-in runnable path is the `main.py` script above, which matches the working ETL behavior in this codebase.
