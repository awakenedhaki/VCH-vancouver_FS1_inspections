# Loading Dependencies =========================================================
import json
import requests

from os import environ
from pathlib import Path
from datetime import datetime

# Constants ====================================================================
# . Paths
RAW_FACILITIES_DIR = Path(environ.get("RAW_FACILITIES_DIR"))

# Timestamp
DATE = datetime.now().strftime("%Y-%m-%d")

if __name__ == "__main__":
    # Request Parameters
    URL = environ.get("FACILITIES_ENDPOINT")
    HEADERS = json.loads(environ.get("HEADERS"))
    TIMEOUT = int(environ.get("TIMEOUT"))

    PAYLOAD = json.dumps(
        {
            "pageNumber": 0,
            "pageSize": 10_689,
            "criteria": "",
            "sort": [{"field": "community", "order": "asc"}],
            "disclosureProgramId": "9b234c07-fdcb-4d9f-a1d6-d5a0d6a77cd8",
            "fields": [],
            "filters": [],
        }
    )

    # Fetching
    with requests.request(
        "POST", URL, headers=HEADERS, data=PAYLOAD, timeout=TIMEOUT
    ) as response:
        response.raise_for_status()
        facilities = response.json()

    # Saving
    with open(RAW_FACILITIES_DIR / f"{DATE}_facilities.json", "w") as f:
        json.dump(facilities, f, indent=2)
