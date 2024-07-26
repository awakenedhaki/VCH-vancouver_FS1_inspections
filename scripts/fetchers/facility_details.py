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
    / f"facility_details_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
)

# Constants ====================================================================
# . Paths
TIMESTAMP = datetime.now().strftime("%Y-%m-%d+%H-%M-%S")

FACILITIES_DIR = Path(environ.get("RAW_FACILITIES_DIR"))
FACILITY_DETAILS_PATH = FACILITIES_DIR / "vancouver_FSE1_details"

# Load Facilities ==============================================================
DATE = "2024-07-12"
FILTER = "vancouver-FSE1"
FACILITIES_PATH = FACILITIES_DIR / f"{DATE}_{FILTER}.json"

with FACILITIES_PATH.open(mode="r") as f:
    facility_ids = [facility["id"] for facility in json.load(f)]


# Helper Functions =============================================================
def custom_payload(id):
    return json.dumps([id])


if __name__ == "__main__":
    # Request Parameters
    URL = environ.get("FACILITY_DETAILS_ENDPOINT")
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
    with fetcher.ThreadedPOSTRequestHandler(
        url=URL,
        headers=HEADERS,
        n_attempts=N_ATTEMPTS,
        timeout=TIMEOUT,
        throttle=THROTTLE,
    ) as handler:
        handler.set_custom_payload(custom_payload)

        facility_details = handler.fetch_all_threaded(
            facility_ids, START, FINISH, N_WORKERS
        )

    # Saving
    filename = f"{TIMESTAMP}_range-{START}-{FINISH - 1}_{DATE}_{FILTER}.json"
    with open(FACILITY_DETAILS_PATH / filename, mode="w") as f:
        json.dump(list(facility_ids), f, indent=2)
