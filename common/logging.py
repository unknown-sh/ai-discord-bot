import logging
from logging.handlers import RotatingFileHandler
import os
import sys
from datetime import datetime

LOG_FILE = os.getenv("LOG_FILE", "bot_actions.log")
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 5 * 1024 * 1024))  # 5 MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 3))

logger = logging.getLogger("bot_logger")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Attempt file handler
try:
    # Try to open the file for appending to check writeability
    with open(LOG_FILE, "a"):
        pass
    handler = RotatingFileHandler(LOG_FILE, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
except Exception as e:
    # Fallback to stdout
    fallback_handler = logging.StreamHandler(sys.stdout)
    fallback_handler.setFormatter(formatter)
    logger.addHandler(fallback_handler)
    logger.warning(f"Failed to initialize file-based logging: {e}. Using stdout fallback.")

def log_action(user_id, action_type, data):
    message = f"User ID: {user_id} | Action: {action_type} | Data: {data}"
    logger.info(message)
