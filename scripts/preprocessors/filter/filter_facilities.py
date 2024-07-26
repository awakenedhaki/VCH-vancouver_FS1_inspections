# Loading Dependencies =========================================================
import re
import json

from os import environ
from pathlib import Path


# Constants ====================================================================
# . Paths
RAW_FACILTIES_DIR = Path(environ.get("RAW_FACILTIES_DIR"))
TMP_FACILTIES_DIR = Path(environ.get("TMP_FACILTIES_DIR"))


# Helper Functions =============================================================
def subset_keys(collection, keys):
    """Returns a new dictionary containing only the specified keys from the given collection.

    Args:
        collection (dict): The dictionary from which to extract the subset of keys.
        keys (list): A list of keys to include in the subset dictionary.

    Returns:
        dict: A new dictionary containing only the specified keys from the original collection.
    """
    return {key: collection[key] for key in keys}


# Load Facilities ==============================================================
DATE = "2024-07-12"
with open(RAW_FACILTIES_DIR / f"{DATE}_facilities.json", "r") as f:
    facilities = json.load(f)


if __name__ == "__main__":
    # Feature
    KEYS = (
        "id",
        "facilityType",
        "facilityName",
        "community",
        "siteAddress",
        "latitude",
        "longitude",
    )

    # Filter for Food Service Establishment 1 facilities in Vancouver
    vancouver_facilities = []
    for facility in facilities["result"]:
        is_FSE1 = facility["facilityType"] == "Food Service Establishment 1"
        is_vancouver = re.match("Vancouver", facility["community"])

        if is_FSE1 and is_vancouver:
            vancouver_facilities.append(subset_keys(facility, KEYS))

    # Saving
    with open(TMP_FACILTIES_DIR / f"{DATE}_vancouver-FSE1.json", "w") as f:
        json.dump(vancouver_facilities, f, indent=2)
