#!/usr/bin/env python3
"""Convert JSON input to CSV using only the Python standard library."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Iterable


class JsonToCsvError(Exception):
    """Raised for user-facing JSON conversion failures."""


def read_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    try:
        return Path(path).read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise JsonToCsvError(f"could not read {path!r}: {exc}") from exc


def load_json(text: str) -> object:
    if not text.strip():
        return []
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise JsonToCsvError(f"invalid JSON: {exc.msg} at line {exc.lineno} column {exc.colno}") from exc


def ordered_fields(rows: list[dict[str, object]], explicit_fields: list[str] | None = None) -> list[str]:
    if explicit_fields:
        return explicit_fields

    fields: list[str] = []
    seen = set()
    for row in rows:
        for key in row:
            text_key = str(key)
            if text_key not in seen:
                seen.add(text_key)
                fields.append(text_key)
    return fields


def cell_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def normalize_object_rows(data: object) -> list[dict[str, object]]:
    if isinstance(data, dict):
        return [{str(key): value for key, value in data.items()}]
    if not isinstance(data, list):
        raise JsonToCsvError("expected a JSON object, array of objects, or array of arrays")
    if not data:
        return []
    if not all(isinstance(row, dict) for row in data):
        raise JsonToCsvError("expected every JSON array item to be an object unless --array-rows is used")
    return [{str(key): value for key, value in row.items()} for row in data]


def normalize_array_rows(data: object) -> list[list[object]]:
    if not isinstance(data, list):
        raise JsonToCsvError("--array-rows requires a top-level JSON array")
    rows: list[list[object]] = []
    for index, row in enumerate(data):
        if not isinstance(row, list):
            raise JsonToCsvError(f"--array-rows expected item {index} to be a JSON array")
        rows.append(row)
    return rows


def write_csv(
    data: object,
    output_path: str | None,
    *,
    explicit_fields: list[str] | None = None,
    array_rows: bool = False,
) -> None:
    output = open(output_path, "w", encoding="utf-8", newline="") if output_path else sys.stdout
    try:
        writer = csv.writer(output)
        if array_rows:
            for row in normalize_array_rows(data):
                writer.writerow([cell_value(value) for value in row])
            return

        rows = normalize_object_rows(data)
        fields = ordered_fields(rows, explicit_fields)
        if fields:
            writer.writerow(fields)
        for row in rows:
            writer.writerow([cell_value(row.get(field)) for field in fields])
    finally:
        if output_path:
            output.close()


def parse_fields(value: str | None) -> list[str] | None:
    if value is None:
        return None
    fields = [field.strip() for field in value.split(",") if field.strip()]
    if not fields:
        raise JsonToCsvError("--fields must include at least one field name")
    return fields


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read JSON from a file or stdin and write CSV.",
    )
    parser.add_argument("input", help="JSON file path, or '-' for stdin")
    parser.add_argument("-o", "--output", help="write CSV to this file")
    parser.add_argument(
        "--fields",
        help="comma-separated object fields/order; missing fields are emitted as empty cells",
    )
    parser.add_argument(
        "--array-rows",
        action="store_true",
        help="treat top-level JSON as an array of arrays and emit rows without a header",
    )
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] = sys.argv[1:]) -> int:
    try:
        args = parse_args(argv)
        data = load_json(read_text(args.input))
        write_csv(
            data,
            args.output,
            explicit_fields=parse_fields(args.fields),
            array_rows=args.array_rows,
        )
    except JsonToCsvError as exc:
        print(f"json_to_csv: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
