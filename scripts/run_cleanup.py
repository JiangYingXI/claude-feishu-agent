"""Delete records older than 90 days from Feishu."""
import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.feishu.cleanup import cleanup_old_records
from src.utils import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("cleanup")


def main():
    try:
        config.validate()
    except RuntimeError as e:
        logger.error(f"Config error: {e}")
        sys.exit(1)

    deleted = cleanup_old_records()
    logger.info(f"Cleanup complete: {deleted} records deleted.")


if __name__ == "__main__":
    main()
