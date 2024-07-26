# Loading Dependencies =========================================================
import json
import logging

from os import environ
from pathlib import Path
from datetime import datetime
from collections import ChainMap
from vchtools import fetcher, logger

# Set up Logging ===============================================================
LOG_DIR = Path(environ.get("LOGS_DIR"))
logger.setup_logging(
    log_file=LOG_DIR
    / f"inspection_reports_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
)

# Constants ====================================================================
# . Paths
TIMESTAMP = datetime.now().strftime("%Y-%m-%d+%H-%M-%S")

RAW_INSPECTION_REPORTS_PATH = Path(environ.get("RAW_REPORT_INSPECTIONS_DIR"))
PROCESSED_REPORTS_DIR = Path(environ.get("PROCESSED_REPORTS_DIR"))

# Load Facilities ==============================================================
DATE = "2024-07-14"
INSPECTION_REPORTS_DETAILS_PATH = (
    PROCESSED_REPORTS_DIR / f"{DATE}_inspection-details.json"
)

with INSPECTION_REPORTS_DETAILS_PATH.open(mode="r") as f:
    inspection_report_entries = json.load(f)

# Filter Facilities ============================================================
N_ENTRIES = 5

inspection_report_ids = []
for facility_id, entries in ChainMap(*inspection_report_entries).items():
    entry_ids = [
        entry["id"] for entry in entries if entry["inspectionType"] == "Routine"
    ]
    if len(entry_ids) < N_ENTRIES:
        continue
    inspection_report_ids.append([facility_id, entry_ids])


if __name__ == "__main__":
    # Request Parameters
    URL = environ.get("INSPECTION_REPORT_ENDPOINT")
    HEADERS = json.loads(environ.get("HEADERS"))
    N_ATTEMPTS = int(environ.get("N_ATTEMPTS"))
    TIMEOUT = int(environ.get("TIMEOUT"))
    THROTTLE = int(environ.get("THROTTLE"))

    # Threading
    N_WORKERS = int(environ.get("N_WORKERS"))

    # Indexing
    START = 2_000
    FINISH = 4_000

    # Fetching
    with fetcher.ThreadedGETRequestHandler(
        url=URL,
        headers=HEADERS,
        n_attempts=N_ATTEMPTS,
        timeout=TIMEOUT,
        throttle=THROTTLE,
    ) as handler:
        facility_reports = []
        logging.info(f"Fetching records in range: [{START}, {FINISH}).")
        for facility_id, entry_ids in inspection_report_ids[START:FINISH]:
            reports = handler.fetch_all_threaded(entry_ids, N_WORKERS)
            facility_reports.append({facility_id: list(zip(entry_ids, reports))})

    # Saving
    with open(
        RAW_INSPECTION_REPORTS_PATH
        / f"{TIMESTAMP}_range-{START}-{FINISH - 1}_inspection_reports.json",
        mode="w",
    ) as f:
        json.dump(facility_reports, f, indent=2)
