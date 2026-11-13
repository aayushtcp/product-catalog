"""Command-line entry point for ``python -m seed``."""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

from alembic import command
from alembic.config import Config

from constants import CATALOG_JSON_PATH_KEY, IMAGES_DIR_KEY
from seed.cleaning import prepare_seed_data
from seed.db import ensure_database
from seed.loader import count_rows, load_seed_data
from seed.parsing import load_catalog

logger = logging.getLogger(__name__)
SRC_DIR = Path(__file__).resolve().parents[1]


def run_migrations() -> None:
    config = Config(str(SRC_DIR / "alembic.ini"))
    config.set_main_option("prepend_sys_path", str(SRC_DIR))
    command.upgrade(config, "head")


def resolve_path(raw_value: str | None, default: str) -> Path:
    """Resolve env paths from cwd, then the api/ and repository roots."""
    value = raw_value or default
    path = Path(value).expanduser()
    if path.is_absolute():
        return path

    module_path = Path(__file__).resolve()
    candidates = [
        Path.cwd() / path,
        module_path.parents[2] / path,  # api/
        module_path.parents[3] / path,  # repository root
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    return candidates[0]


async def run() -> None:
    catalog_path = resolve_path(
        os.getenv(CATALOG_JSON_PATH_KEY),
        "../data/catalog.json",
    )
    if not catalog_path.exists():
        raise FileNotFoundError(
            f"catalog.json not found. Looked for {catalog_path}. "
            f"Set {CATALOG_JSON_PATH_KEY} in api/.env."
        )

    images_path = resolve_path(
        os.getenv(IMAGES_DIR_KEY),
        "../data/images",
    )
    if not images_path.is_dir():
        logger.warning("Images directory not found at %s", images_path)

    logger.info("Reading catalog from %s", catalog_path)
    catalog = load_catalog(catalog_path)
    data = prepare_seed_data(catalog)

    for issue in data.issues:
        logger.warning(issue)

    await load_seed_data(data)

    counts = await count_rows()
    logger.info("Seed complete")
    for table, count in counts.items():
        logger.info("%-20s %s", table, count)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(message)s",
    )
    ensure_database()
    run_migrations()
    asyncio.run(run())


if __name__ == "__main__":
    main()
