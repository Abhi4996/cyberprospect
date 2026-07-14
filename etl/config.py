import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "input")
DATA_DIR = os.path.join(BASE_DIR, "data")
PARQUET_DIR = os.path.join(DATA_DIR, "parquet")
DUCKDB_PATH = os.path.join(DATA_DIR, "cyberprospect.duckdb")

# Shodan full file is test_scans.json.zst, sample is test_scans_sample.json
INPUT_FILE = os.path.join(INPUT_DIR, "test_scans_sample.json")  # default to sample for testing
# To use a different file, uncomment and update the path below:
# INPUT_FILE = r"E:\shodan_assignment\input\test_scans_sample.json"

EXCLUDE_ORGS = [
    "Google LLC", "Amazon.com, Inc.", "Cloudflare, Inc.",
    "Microsoft Corporation", "DigitalOcean, LLC",
    "OVH SAS", "Hetzner Online AG", "Linode",
    "Incapsula Inc", "Fastly, Inc.", "Akamai Technologies",
]
