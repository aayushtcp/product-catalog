"""Create the configured database for the seed command."""

from __future__ import annotations

import logging

import psycopg
from psycopg import sql

from database import DB_SETTINGS

logger = logging.getLogger(__name__)


def ensure_database() -> None:
    """Create the configured database when it does not exist yet."""
    settings = {key: value for key, value in DB_SETTINGS.items() if key != "dbname"}
    database_name = DB_SETTINGS["dbname"]

    try:
        with psycopg.connect(
            dbname="postgres",
            autocommit=True,
            **settings,
        ) as connection:
            exists = connection.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (database_name,),
            ).fetchone()
            if exists:
                logger.info("Database %s already exists", database_name)
                return

            statement = sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(database_name)
            )
            connection.execute(statement)
            logger.info("Created database %s", database_name)
    except psycopg.errors.DuplicateDatabase:
        logger.info("Database %s already exists", database_name)
    except psycopg.OperationalError as error:
        logger.warning(
            "Could not verify/create database %s: %s",
            database_name,
            error,
        )
