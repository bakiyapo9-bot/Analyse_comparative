import logging
from config import LOGS_DIR, JOURNAL_FILE

def obtenir_logger():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("comparateur")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(JOURNAL_FILE, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(handler)
    return logger

def anomalie(message):
    obtenir_logger().warning(message)
