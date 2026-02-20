import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "trading_bot.log")


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure logging to both console and rotating log file."""
    os.makedirs(LOG_DIR, exist_ok=True)

    log_level = getattr(logging, level.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root_logger = logging.getLogger("trading_bot")
    root_logger.setLevel(log_level)

    # Avoid adding duplicate handlers on re-import
    if root_logger.handlers:
        return root_logger

    # File handler (rotating, max 5 MB × 3 backups)
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)  # keep console quiet; details go to file

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return root_logger
