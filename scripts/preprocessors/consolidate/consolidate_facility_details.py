# Loading Dependencies =========================================================
from os import environ
from pathlib import Path
from vchtools import consolidator


# Constants ====================================================================
# . Paths
RAW_FACILITIES_DIR = Path(environ.get("RAW_FACILITIES_DIR"))
RAW_FACILITY_DETAILS_DIR = RAW_FACILITIES_DIR / "vancouver_FSE1_details"

PROCESSED_FACILITIES_DIR = Path(environ.get("PROCESSED_FACILITIES_DIR"))


# Consolidate Facility Details Data ============================================
facility_details = consolidator.load_data_from_json(RAW_FACILITY_DETAILS_DIR)
consolidator.save_data_to_json(
    facility_details, PROCESSED_FACILITIES_DIR, "vancouver_FSE1_details"
)
