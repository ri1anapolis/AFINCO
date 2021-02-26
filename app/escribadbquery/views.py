# pylint: disable=missing-docstring,empty-docstring
import os
import logging
from mysql.connector import MySQLConnection, Error
from sentry_sdk import capture_exception

logger = logging.getLogger("afinco")


def query_with_fetchall(query):
    """Get data from database."""

    try:
        db_config = {
            "host": os.getenv("REGISTER_HOST", "localhost"),
            "port": os.getenv("REGISTER_PORT", "3306"),
            "database": os.getenv("REGISTER_DB", "sqlreg3"),
            "user": os.getenv("REGISTER_USER", "mysql"),
            "password": os.getenv("REGISTER_PASSWORD", "mysql"),
        }
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        rows_count = cursor.rowcount

    except Error as error:
        logger.error("REGISTER ::: Database Error: %s", error)
        capture_exception(error)
        raise Exception from error

    finally:
        cursor.close()
        conn.close()

    return rows, rows_count
