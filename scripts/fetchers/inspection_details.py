# Loading Dependencies =========================================================
import json

from os import environ
from pathlib import Path
from datetime import datetime
from vchtools import fetcher, logger

# Set up Logging ===============================================================
LOG_DIR = Path(environ.get("LOGS_DIR"))
logger.setup_logging(
    log_file=LOG_DIR
    / f"inspection_details_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
)

# Constants ====================================================================
# . Paths
TIMESTAMP = datetime.now().strftime("%Y-%m-%d+%H-%M-%S")

RAW_REPORTS_DETAILS_DIR = Path(environ.get("RAW_REPORT_DETAILS_DIR"))

# Load Facilities ==============================================================
DATE = "2024-07-12"
FILTER = "vancouver-FSE1"
FACILITIES_PATH = Path(environ.get("RAW_FACILITIES_DIR")) / f"{DATE}_{FILTER}.json"

with FACILITIES_PATH.open(mode="r") as f:
    facility_ids = [facility["id"] for facility in json.load(f)]


if __name__ == "__main__":
    # Request Parameters
    BASE_URL = environ.get("INSPECTION_DETAILS_ENDPOINT")
    HEADERS = json.loads(environ.get("HEADERS"))
    N_ATTEMPTS = int(environ.get("N_ATTEMPTS"))
    TIMEOUT = int(environ.get("TIMEOUT"))
    THROTTLE = int(environ.get("THROTTLE"))

    # Threading
    N_WORKERS = int(environ.get("N_WORKERS"))

    # Indexing
    START = 0
    FINISH = 2

    # Fetching
    with fetcher.ThreadedGETRequestHandler(
        url=BASE_URL,
        headers=HEADERS,
        n_attempts=N_ATTEMPTS,
        timeout=TIMEOUT,
        throttle=THROTTLE,
    ) as handler:
        report_entries = handler.fetch_all_threaded(
            ids=facility_ids,
            start=START,
            finish=FINISH,
            n_workers=N_WORKERS,
        )

    # Saving
    with open(
        RAW_REPORTS_DETAILS_DIR
        / f"{TIMESTAMP}_{FILTER}_range-{START}-{FINISH - 1}_inspection_details.json",
        mode="w",
    ) as f:
        json.dump(list(report_entries), f, indent=2)
