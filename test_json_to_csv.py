import csv
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from json_to_csv import load_json, write_csv


class JsonToCsvTests(unittest.TestCase):
    def render(self, data, **kwargs):
        stream = io.StringIO(newline="")
        original_stdout = sys.stdout
        try:
            sys.stdout = stream
            write_csv(data, None, **kwargs)
        finally:
            sys.stdout = original_stdout
        return list(csv.reader(io.StringIO(stream.getvalue())))

    def test_array_of_objects_with_union_header_and_unicode(self):
        data = load_json('[{"name":"Ada","city":"Zürich"},{"name":"Bob","score":42}]')
        rows = self.render(data)
        self.assertEqual(rows[0], ["name", "city", "score"])
        self.assertEqual(rows[1], ["Ada", "Zürich", ""])
        self.assertEqual(rows[2], ["Bob", "", "42"])

    def test_explicit_fields_and_nested_values(self):
        data = load_json('[{"id":1,"meta":{"ok":true},"tags":["a","b"]}]')
        rows = self.render(data, explicit_fields=["id", "tags", "meta", "missing"])
        self.assertEqual(rows[0], ["id", "tags", "meta", "missing"])
        self.assertEqual(rows[1], ["1", '["a","b"]', '{"ok":true}', ""])

    def test_single_object(self):
        rows = self.render({"name": "Ada", "score": 99})
        self.assertEqual(rows, [["name", "score"], ["Ada", "99"]])

    def test_array_rows_mode(self):
        rows = self.render([["name", "score"], ["Ada", 99]], array_rows=True)
        self.assertEqual(rows, [["name", "score"], ["Ada", "99"]])

    def test_cli_writes_valid_csv_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            json_path = Path(tmp) / "input.json"
            csv_path = Path(tmp) / "output.csv"
            json_path.write_text('[{"name":"Ada","score":99}]', encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "json_to_csv.py", str(json_path), "--output", str(csv_path)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            with csv_path.open(encoding="utf-8", newline="") as handle:
                self.assertEqual(list(csv.reader(handle)), [["name", "score"], ["Ada", "99"]])

    def test_invalid_json_returns_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            json_path = Path(tmp) / "bad.json"
            json_path.write_text("{bad", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "json_to_csv.py", str(json_path)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid JSON", result.stderr)


if __name__ == "__main__":
    unittest.main()
