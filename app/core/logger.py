"""
ResearchPilot Edge - Logging Framework
Provides structured timestamped logging to console and file for execution telemetry.
"""

import logging
import sys
from pathlib import Path

# Configure format
LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s:%(lineno)d - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def get_logger(name: str = "ResearchPilot") -> logging.Logger:
    """Returns a configured logger instance."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
        logger.addHandler(handler)
    return logger

logger = get_logger("ResearchPilot.Core")
