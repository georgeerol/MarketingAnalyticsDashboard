"""
Logging configuration for the application.
"""

import logging
import sys

from app.core.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """Configure application logging."""
    
    # Define log format
    log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "%(filename)s:%(lineno)d - %(message)s"
    )
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific logger levels
    loggers_config = {
        "uvicorn": "INFO",
        "uvicorn.access": "INFO",
        "sqlalchemy.engine": "WARNING",
        "sqlalchemy.pool": "WARNING",
        "app": settings.LOG_LEVEL.upper(),
    }
    
    for logger_name, level in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, level))


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)
