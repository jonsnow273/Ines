"""
Centralized logging for Ines.
Configures structured file and console logging with automatic fallback.
"""

import os
import sys
import logging
from pathlib import Path
from core.constants import LOGS_DIR

LOG_FILE_PATH = LOGS_DIR / "ines.log"

try:
    from loguru import logger as _loguru_logger
    _USE_LOGURU = True
except ImportError:
    _USE_LOGURU = False

if _USE_LOGURU:
    # Configure Loguru
    _loguru_logger.remove()  # Remove default handler

    # Console Handler (Colorized, concise)
    _loguru_logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True,
    )

    # File Handler (Detailed, rotating)
    _loguru_logger.add(
        str(LOG_FILE_PATH),
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        encoding="utf-8",
    )
    logger = _loguru_logger

else:
    # Standard library logging fallback
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),
            logging.FileHandler(str(LOG_FILE_PATH), encoding="utf-8"),
        ],
    )
    logger = logging.getLogger("ines")


def set_log_level(level: str) -> None:
    """Dynamically set logging level (DEBUG, INFO, WARNING, ERROR)."""
    level = level.upper()
    if _USE_LOGURU:
        # Reconfigure loguru level
        logger.remove()
        logger.add(
            sys.stderr,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=level,
            colorize=True,
        )
        logger.add(
            str(LOG_FILE_PATH),
            rotation="10 MB",
            retention="7 days",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            encoding="utf-8",
        )
    else:
        std_level = getattr(logging, level, logging.INFO)
        logger.setLevel(std_level)
