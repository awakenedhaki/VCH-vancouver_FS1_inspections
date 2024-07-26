# Loading Dependencies =========================================================
from os import environ
from pathlib import Path
from vchtools import consolidator


# Constants ===================================================================
RAW_REPORT_DETAILS_DIR = Path(environ.get("RAW_REPORT_DETAILS_DIR"))
PROCESSED_REPORTS_DIR = Path(environ.get("PROCESSED_REPORTS_DIR"))


# Consolidate Inspection Report Entries ========================================
inspection_report_details = consolidator.load_data_from_json(RAW_REPORT_DETAILS_DIR)
consolidator.save_data_to_json(
    inspection_report_details, PROCESSED_REPORTS_DIR, "inspection-details"
)
