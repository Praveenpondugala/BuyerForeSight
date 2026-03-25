# app/core/logging.py
import logging
import sys
from app.core.config import settings


def setup_logger(name: str = "buyerforesight") -> logging.Logger:
    log = logging.getLogger(name)
    log.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    if not log.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
        )
        log.addHandler(handler)

    log.propagate = False
    return log


logger = setup_logger()
