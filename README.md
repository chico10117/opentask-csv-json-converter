# CSV to JSON Converter

Submission-ready artifact for OpenTask CSV-to-JSON tasks:

- `cmp545xcw001bl704p3a7ock7`
- `cmp545t0n0011l704htzztdbb`

## Run

```sh
python3 csv_to_json.py input.csv
python3 csv_to_json.py input.csv --indent 0
python3 csv_to_json.py input.csv --delimiter ';' --output output.json
python3 csv_to_json.py --no-header input.csv
```

## Verify

```sh
python3 -m unittest -v test_csv_to_json.py
```

The script uses only the Python standard library.
