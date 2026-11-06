"""Run with python -m titanic_summary PATH."""

import argparse
import csv
import json
import sys
from pathlib import Path


def summarize(path: Path) -> dict:
    """Validate records and return fractional rates rounded to six places."""
    counts = {}
    survivors = {}
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, strict=True)
        required = {"Survived", "Pclass"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("Duplicate CSV column names")
        for row in reader:
            if None in row or None in row.values():
                raise ValueError(
                    f"Row ending at line {reader.line_num}: inconsistent columns"
                )
            for column, allowed in (
                ("Survived", {"0", "1"}),
                ("Pclass", {"1", "2", "3"}),
            ):
                if row[column] not in allowed:
                    raise ValueError(
                        f"Row ending at line {reader.line_num}: {column} must be "
                        f"one of {', '.join(sorted(allowed))}; got {row[column]!r}"
                    )
            passenger_class = row["Pclass"]
            counts[passenger_class] = counts.get(passenger_class, 0) + 1
            survivors[passenger_class] = survivors.get(passenger_class, 0) + int(
                row["Survived"]
            )
    total = sum(counts.values())
    if not total:
        raise ValueError("CSV contains no passenger records")
    total_survivors = sum(survivors.values())
    return {
        "total_passengers": total,
        "total_survivors": total_survivors,
        "survival_rate": round(total_survivors / total, 6),
        "classes": {
            key: {
                "passenger_count": counts[key],
                "survival_rate": round(survivors[key] / counts[key], 6),
            }
            for key in sorted(counts)
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize Titanic passenger survival")
    parser.add_argument(
        "csv_path", type=Path, help="CSV with Survived and Pclass columns"
    )
    args = parser.parse_args(argv)
    try:
        result = summarize(args.csv_path)
    except (OSError, UnicodeError, ValueError, csv.Error) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
