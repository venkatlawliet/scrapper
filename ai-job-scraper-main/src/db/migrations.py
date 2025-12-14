import logging
from alembic import command
from alembic.config import Config
from alembic.util.exc import CommandError
from sqlalchemy.exc import SQLAlchemyError
logger = logging.getLogger(__name__)
def run_migrations() -> None:
    try:
        logger.info("Starting database migrations...")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully")
    except (CommandError, SQLAlchemyError) as e:
        logger.exception(
            "Failed to run database migrations [%s]",
            type(e).__name__,
        )
        logger.warning(
            "Application will continue with current database schema. "
            "Manual migration may be required.",
        )