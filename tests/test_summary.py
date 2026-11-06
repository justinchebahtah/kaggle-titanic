import json
import subprocess
import sys
from pathlib import Path

import pytest

from titanic_summary.__main__ import main, summarize

FIXTURE = Path(__file__).parent / "fixtures" / "passengers.csv"


def test_calculations():
    assert summarize(FIXTURE) == {
        "total_passengers": 6,
        "total_survivors": 3,
        "survival_rate": 0.5,
        "classes": {
            "1": {"passenger_count": 2, "survival_rate": 1.0},
            "2": {"passenger_count": 2, "survival_rate": 0.5},
            "3": {"passenger_count": 2, "survival_rate": 0.0},
        },
    }


def test_cli_deterministic():
    command = [sys.executable, "-m", "titanic_summary", str(FIXTURE)]
    first = subprocess.run(command, capture_output=True, text=True, check=True)
    second = subprocess.run(command, capture_output=True, text=True, check=True)
    assert first.stdout == second.stdout
    assert first.stderr == ""
    assert (
        first.stdout == json.dumps(summarize(FIXTURE), indent=2, sort_keys=True) + "\n"
    )


def test_missing_file(tmp_path, capsys):
    assert main([str(tmp_path / "missing.csv")]) == 1
    result = capsys.readouterr()
    assert result.out == ""
    assert "No such file" in result.err


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("Pclass\n1\n", "Missing required columns: Survived"),
        ("Survived\n1\n", "Missing required columns: Pclass"),
        ("", "Missing required columns"),
        ("Survived,Pclass\n", "no passenger records"),
        ("Survived,Pclass\n2,1\n", "Survived must be"),
        ("Survived,Pclass\n1,4\n", "Pclass must be"),
        ("Survived,Pclass\n,1\n", "Survived must be"),
        ("Survived,Pclass\n1,\n", "Pclass must be"),
        ("Survived,Pclass\ntrue,1\n", "Survived must be"),
        ("Survived,Pclass\n1,1.0\n", "Pclass must be"),
        ("Survived,Pclass\n1\n", "inconsistent columns"),
        ("Survived,Pclass\n1,1,extra\n", "inconsistent columns"),
        ("Survived,Pclass,Pclass\n1,1,1\n", "Duplicate CSV"),
        ('Survived,Pclass\n"1,1\n', "unexpected end of data"),
    ],
)
def test_invalid_input(tmp_path, capsys, content, message):
    source = tmp_path / "input.csv"
    source.write_text(content)
    assert main([str(source)]) == 1
    result = capsys.readouterr()
    assert result.out == ""
    assert message in result.err


def test_single_class_and_rounding(tmp_path):
    source = tmp_path / "input.csv"
    source.write_text("Survived,Pclass\n1,3\n0,3\n0,3\n")
    result = summarize(source)
    assert result["survival_rate"] == 0.333333
    assert result["classes"] == {"3": {"passenger_count": 3, "survival_rate": 0.333333}}


def test_invalid_encoding(tmp_path, capsys):
    source = tmp_path / "input.csv"
    source.write_bytes(b"\xff")
    assert main([str(source)]) == 1
    assert "error:" in capsys.readouterr().err
