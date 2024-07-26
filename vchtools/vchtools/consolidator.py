import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


def load_data_from_json(
    directory_path: Path, pattern: str = "*.json"
) -> List[Dict[str, Any]]:
    """Loads data from JSON files in a given directory.

    Args:
        directory_path (Path): The path to the directory containing the JSON files.
        pattern (str, optional): The file pattern to match. Defaults to "*.json".

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing the loaded data from the JSON files.
    """
    data: List[Dict[str, Any]] = []
    for file_path in directory_path.glob(pattern):
        with open(file_path, "r") as f:
            data.extend(json.load(f))
    return data


def save_data_to_json(
    data: List[Dict[str, Any]], save_directory: str, filename_suffix: str
) -> None:
    """Saves the given data to a JSON file.

    Args:
        data (Any): The data to be saved.
        save_directory (str): The directory where the file will be saved.
        filename_suffix (str): The suffix to be added to the filename.

    Returns:
        None
    """
    date: str = datetime.now().strftime("%Y-%m-%d")
    filename: str = f"{date}_{filename_suffix}.json"
    with open(Path(save_directory) / filename, "w") as f:
        json.dump(data, f, indent=2)
