import pytest
from typer.testing import CliRunner
from cli import app
from pathlib import Path

runner = CliRunner()


def test_convert_no_files(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    result = runner.invoke(app, ["--input", str(input_dir)])
    assert result.exit_code == 0
    assert "No .fb2 files found" in result.stdout


def test_convert_success(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    # Create a dummy FB2 file
    fb2_file = input_dir / "test.fb2"
    fb2_file.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
        <FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" xmlns:l="http://www.w3.org/1999/xlink">
            <description><title-info><book-title>Test</book-title></title-info></description>
            <body><section><title><p>Ch1</p></title><p>Text</p></section></body>
        </FictionBook>""",
        encoding="utf-8",
    )

    output_dir = tmp_path / "output"

    result = runner.invoke(
        app, ["--input", str(input_dir), "--output", str(output_dir)]
    )

    assert result.exit_code == 0
    assert "Found 1 files to convert" in result.stdout
    assert "Conversion complete. 1/1 files converted" in result.stdout
    assert (output_dir / "test.epub").exists()


def test_convert_missing_input_dir():
    result = runner.invoke(app, ["--input", "nonexistent_dir"])
    assert result.exit_code != 0
    # Typer/Click prints validation errors to stderr, which is captured in result.output
    # The output is formatted with Rich, so exact string matching is tricky.
    assert "Error" in result.output
