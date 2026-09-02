from contextlib import contextmanager

from psycopg import Connection, OperationalError
from psycopg_pool import ConnectionPool, PoolTimeout

from app.core.errors import DatabaseError
from psycopg.errors import QueryCanceled
import logging
from app.core.config import DATABASE_URL


logger = logging.getLogger(__name__)


def configure_connection(connection: Connection):
    connection.execute(
        "SET statement_timeout = '2000ms';"
    )
    connection.commit()

pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=2,
    max_size=5,
    timeout=5,
    configure=configure_connection,
    open=True,
)


@contextmanager
def get_connection():
    try:
        with pool.connection() as connection:
            yield connection

    except PoolTimeout as error:
        logger.exception("Database connection pool exhausted")
        raise DatabaseError(
            message="Database connection pool exhausted",
            retryable=True,
        ) from error

    except QueryCanceled as error:
        logger.exception("Database query timed out")
        raise DatabaseError(
            message="Database query timed out",
            retryable=True,
        ) from error

    except OperationalError as error:
        logger.exception("Unable to connect to PostgreSQL")
        raise DatabaseError(
            message="Unable to connect to PostgreSQL",
            retryable=True,
        ) from error