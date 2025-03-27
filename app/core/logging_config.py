import logging
import sys
from typing import Dict, Any


def get_logging_config() -> Dict[str, Any]:
    """Return a logging configuration dictionary suitable for dictConfig"""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                # Changed from "%(levelprefix)s %(asctime)s | %(message)s" to standard format
                "format": "%(levelname)s %(asctime)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "weather_service": {"handlers": ["default"], "level": "INFO"},
            "uvicorn": {"handlers": ["default"], "level": "INFO"},
            "uvicorn.error": {"handlers": ["default"], "level": "INFO"},
        },
    }


def setup_logging():
    """Setup logging configuration"""
    logging_config = get_logging_config()
    logging.config.dictConfig(logging_config)


def get_logger(name: str = "weather_service") -> logging.Logger:
    """Get logger by name"""
    return logging.getLogger(name)
