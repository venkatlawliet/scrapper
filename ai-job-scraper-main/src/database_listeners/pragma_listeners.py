import logging
from src.config import Settings
settings = Settings()
logger = logging.getLogger(__name__)
def apply_pragmas(conn, _):
    cursor = conn.cursor()
    for pragma in settings.sqlite_pragmas:
        try:
            cursor.execute(pragma)
            logger.debug("Applied SQLite pragma: %s", pragma)
        except Exception:
            logger.warning("Failed to apply pragma '%s'", pragma)
    cursor.close()