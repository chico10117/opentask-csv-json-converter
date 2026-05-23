import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from csv_to_json import convert_csv_text


class CsvToJsonTests(unittest.TestCase):
    def test_comma_csv_with_quoting_and_unicode(self):
        rows = convert_csv_text(
            'name,city,note\n"Ada, Jr.",Zürich,"line one\nline two"\n'
        )
        self.assertEqual(
            rows,
            [
                {
                    "name": "Ada, Jr.",
                    "city": "Zürich",
                    "note": "line one\nline two",
                }
            ],
        )

    def test_semicolon_delimiter_detection(self):
        rows = convert_csv_text("name;amount\nalice;10\nbob;20\n")
        self.assertEqual(rows, [{"name": "alice", "amount": "10"}, {"name": "bob", "amount": "20"}])

    def test_no_header_rows(self):
        rows = convert_csv_text("a,b\nc,d\n", force_header=False)
        self.assertEqual(rows, [["a", "b"], ["c", "d"]])

    def test_cli_writes_valid_json_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "input.csv"
            json_path = Path(tmp) / "output.json"
            csv_path.write_text("name,score\nAda,99\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "csv_to_json.py", str(csv_path), "--output", str(json_path)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), [{"name": "Ada", "score": "99"}])

    def test_missing_file_returns_error(self):
        result = subprocess.run(
            [sys.executable, "csv_to_json.py", "does-not-exist.csv"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("could not read", result.stderr)


if __name__ == "__main__":
    unittest.main()
