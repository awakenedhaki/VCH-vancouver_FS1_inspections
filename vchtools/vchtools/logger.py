import logging
from typing import Optional, List


def setup_logging(
    log_level: int = logging.INFO, log_file: Optional[str] = None
) -> None:
    """Set up logging configuration.

    Args:
        log_level (int): The logging level to set. Defaults to logging.INFO.
        log_file (str): The path to the log file. If provided, logs will be written to this file.
            Defaults to None.

    Returns:
        None
    """
    handlers: List[logging.Handler] = [logging.StreamHandler()]
    if log_file:
        handlers.append(
            logging.FileHandler(filename=log_file, mode="w", encoding="utf-8")
        )

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )
