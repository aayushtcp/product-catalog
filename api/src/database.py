# Standard library imports
import logging
import os
import traceback

# Third-party library imports
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

# Project-specific imports
from constants import (
    DB_HOST_KEY,
    DB_NAME_KEY,
    DB_PASSWORD_KEY,
    DB_PORT_KEY,
    DB_USER_KEY,
)

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables (defaults work for a local Postgres)
db_host = os.getenv(DB_HOST_KEY, "localhost")
db_port = os.getenv(DB_PORT_KEY, "5432")
db_name = os.getenv(DB_NAME_KEY, "product_catalog")
db_user = os.getenv(DB_USER_KEY, "postgres")
db_password = os.getenv(DB_PASSWORD_KEY, "postgres")

# Connection settings shared by the async engine and the seed's database check.
DB_SETTINGS = {
    "host": db_host,
    "port": int(db_port),
    "user": db_user,
    "password": db_password,
    "dbname": db_name,
}

# SQLAlchemy URL for local PostgreSQL (psycopg driver)
DATABASE_URL = (
    f"postgresql+psycopg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
)

# Initialize the async engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Create an async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Declare base class for all models
Base = declarative_base()


async def get_db():
    """
    Dependency function to provide an asynchronous database session.

    Yields:
        AsyncSession: An active SQLAlchemy AsyncSession for use in async routes/services.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            logging.error("Database error:\n%s", traceback.format_exc())
            raise
        finally:
            await session.close()
