# CSV/JSON Converter

Submission-ready artifact for OpenTask CSV/JSON conversion tasks:

- `cmp545xcw001bl704p3a7ock7`
- `cmp545t0n0011l704htzztdbb`
- `cmpupoqmm0027kw04351wcfhz`

## Run

```sh
python3 csv_to_json.py input.csv
python3 csv_to_json.py input.csv --indent 0
python3 csv_to_json.py input.csv --delimiter ';' --output output.json
python3 csv_to_json.py --no-header input.csv

python3 json_to_csv.py input.json
python3 json_to_csv.py input.json --fields id,name,total --output output.csv
python3 json_to_csv.py - < input.json
```

## Verify

```sh
python3 -m unittest -v test_csv_to_json.py
python3 -m unittest -v test_json_to_csv.py
```

The scripts use only the Python standard library.
