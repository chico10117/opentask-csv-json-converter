#!/usr/bin/env python3
"""Convert CSV input to JSON using only the Python standard library."""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path
from typing import Iterable, TextIO


class CsvToJsonError(Exception):
    """Raised for user-facing CSV conversion failures."""


def read_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    try:
        return Path(path).read_text(encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise CsvToJsonError(f"could not read {path!r}: {exc}") from exc


def detect_dialect(sample: str, delimiter: str | None) -> csv.Dialect:
    if delimiter:
        class ExplicitDialect(csv.excel):
            pass

        ExplicitDialect.delimiter = delimiter
        return ExplicitDialect

    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        return csv.excel


def has_header(sample: str, dialect: csv.Dialect) -> bool:
    try:
        return csv.Sniffer().has_header(sample)
    except csv.Error:
        return True


def convert_csv_text(
    text: str,
    *,
    delimiter: str | None = None,
    force_header: bool | None = None,
) -> list[dict[str, str] | list[str]]:
    if not text.strip():
        return []

    sample = text[:4096]
    dialect = detect_dialect(sample, delimiter)
    use_header = has_header(sample, dialect) if force_header is None else force_header
    stream = io.StringIO(text, newline="")

    try:
        if use_header:
            reader = csv.DictReader(stream, dialect=dialect)
            if not reader.fieldnames:
                return []
            rows = []
            for row in reader:
                normalized = {
                    str(key if key is not None else ""): "" if value is None else value
                    for key, value in row.items()
                }
                rows.append(normalized)
            return rows

        reader = csv.reader(stream, dialect=dialect)
        return [list(row) for row in reader]
    except csv.Error as exc:
        raise CsvToJsonError(f"invalid CSV: {exc}") from exc


def write_json(data: object, output_path: str | None, indent: int | None) -> None:
    kwargs = {
        "ensure_ascii": False,
        "indent": indent,
    }
    if output_path:
        with Path(output_path).open("w", encoding="utf-8", newline="\n") as file:
            json.dump(data, file, **kwargs)
            file.write("\n")
        return

    json.dump(data, sys.stdout, **kwargs)
    sys.stdout.write("\n")


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read CSV from a file or stdin and write JSON.",
    )
    parser.add_argument("input", help="CSV file path, or '-' for stdin")
    parser.add_argument("-o", "--output", help="write JSON to this file")
    parser.add_argument(
        "--delimiter",
        help="override delimiter detection, e.g. ',' ';' tab or '|'",
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="treat rows as arrays instead of using the first row as object keys",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation; use 0 for compact output",
    )
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] = sys.argv[1:]) -> int:
    args = parse_args(argv)
    indent = None if args.indent == 0 else args.indent
    try:
        text = read_text(args.input)
        data = convert_csv_text(
            text,
            delimiter=args.delimiter,
            force_header=False if args.no_header else None,
        )
        write_json(data, args.output, indent)
    except CsvToJsonError as exc:
        print(f"csv_to_json: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
