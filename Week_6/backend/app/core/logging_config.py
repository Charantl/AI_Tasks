import logging
from logging.handlers import RotatingFileHandler
import sys
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "app.log")

# Create a rotating file handler
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
file_handler.setLevel(LOG_LEVEL)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
))

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(LOG_LEVEL)
console_handler.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
))

# Root logger config
logging.basicConfig(
    level=LOG_LEVEL,
    handlers=[file_handler, console_handler],
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name) 