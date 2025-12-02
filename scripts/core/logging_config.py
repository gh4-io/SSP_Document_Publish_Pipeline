"""
Centralized logging configuration for SSP document automation pipeline.

Provides structured logging to both console and file with rotation.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
import sys


def setup_logging(
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    Configure centralized logging for the pipeline.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files (default: ./logs)
        console_output: Whether to output to console (default: True)

    Returns:
        Configured root logger

    Example:
        >>> from scripts.core.logging_config import setup_logging
        >>> logger = setup_logging()
        >>> logger.info("Pipeline started")
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Define log format
    log_format = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(log_format)
        logger.addHandler(console_handler)

    # File handler with rotation
    if log_dir is None:
        log_dir = Path(__file__).parent.parent.parent / "logs"

    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "ssp_pipeline.log"

    # Rotating file handler (daily rotation, keep 30 days)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file,
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing document")
    """
    return logging.getLogger(name)


# Module-level configuration
if __name__ == "__main__":
    # Test logging configuration
    logger = setup_logging(log_level="DEBUG")
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    print(f"\nLog file location: {Path(__file__).parent.parent.parent / 'logs' / 'ssp_pipeline.log'}")
