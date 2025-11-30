"""Logging setup and utilities.

Provides standardized logging configuration for the SSP pipeline.
Part of SSP Document Publishing Pipeline v4.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logger(name: str, log_dir: Optional[Path] = None, level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return a logger for the SSP pipeline.

    Args:
        name: Logger name (typically __name__ from calling module)
        log_dir: Directory for log files. If None, logs to console only
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance

    Raises:
        OSError: If log_dir cannot be created
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers if logger already configured
    if logger.handlers:
        return logger

    # Format: [YYYY-MM-DD HH:MM:SS] [LEVEL] [module] message
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler (always present)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"ssp_pipeline_{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def log_pipeline_start(markdown_path: Path, profile_path: Path) -> None:
    """
    Log pipeline execution start with input parameters.

    Args:
        markdown_path: Path to source Markdown file
        profile_path: Path to layout profile JSON
    """
    logger = logging.getLogger("ssp_pipeline")
    logger.info("=" * 60)
    logger.info("SSP Document Publishing Pipeline - Execution Start")
    logger.info(f"Markdown source: {markdown_path}")
    logger.info(f"Layout profile: {profile_path}")
    logger.info("=" * 60)


def log_pipeline_complete(output_path: Path, duration_seconds: float) -> None:
    """
    Log successful pipeline completion.

    Args:
        output_path: Path to generated output file
        duration_seconds: Total execution time
    """
    logger = logging.getLogger("ssp_pipeline")
    logger.info("=" * 60)
    logger.info("Pipeline completed successfully")
    logger.info(f"Output file: {output_path}")
    logger.info(f"Duration: {duration_seconds:.2f} seconds")
    logger.info("=" * 60)
