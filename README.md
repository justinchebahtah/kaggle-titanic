# Titanic Passenger Summary

A small standard-library Python CLI for summarizing passenger survival from CSV.
The included data is synthetic; no Kaggle account or downloads are needed.

## Development setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```sh
uv sync --locked --python 3.12
```

The committed `uv.lock` pins development dependencies. The application itself has
no third-party dependencies. If the default uv cache is read-only, first run
`export UV_CACHE_DIR=/tmp/titanic-uv-cache`.

## Usage

```sh
uv run python -m titanic_summary tests/fixtures/passengers.csv
```

Expected output:

```json
{
  "classes": {
    "1": {
      "passenger_count": 2,
      "survival_rate": 1.0
    },
    "2": {
      "passenger_count": 2,
      "survival_rate": 0.5
    },
    "3": {
      "passenger_count": 2,
      "survival_rate": 0.0
    }
  },
  "survival_rate": 0.5,
  "total_passengers": 6,
  "total_survivors": 3
}
```

Input must be UTF-8 CSV (an optional BOM is accepted) with unique column names
including `Survived` and `Pclass`. `Survived` must be exactly `0` or `1`, and
`Pclass` exactly `1`, `2`, or `3`. Additional columns are allowed; each record must
have the same number of fields as the header. Blank lines are ignored.

Rates are fractions from 0 to 1 rounded to six decimal places. Only classes present
in the input are reported. JSON keys are sorted with two-space indentation.
Missing or unreadable files, invalid CSV/encoding, missing columns, no passenger
records, and invalid values produce a clear error on stderr and exit code 1,
without JSON output. Invalid command-line arguments exit with code 2.

## Checks

```sh
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
```

GitHub Actions runs these checks with Python 3.12 and uv 0.13.5 after a locked
sync. Tests cover aggregate and per-class results, rounding, deterministic CLI
output, missing files/columns, empty inputs, invalid values, malformed records,
duplicate headers, and invalid encoding.

The repository originally described a Random Forest Titanic experiment. This
pilot implements a CSV summary tool; it does not train a model.
