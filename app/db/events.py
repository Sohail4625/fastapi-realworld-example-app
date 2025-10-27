import asyncpg
from fastapi import FastAPI
import structlog
from app.core.settings.app import AppSettings


log = structlog.get_logger()

async def connect_to_db(app: FastAPI, settings: AppSettings) -> None:
    log.info("Connecting to PostgreSQL")

    app.state.pool = await asyncpg.create_pool(
        str(settings.database_url),
        min_size=settings.min_connection_count,
        max_size=settings.max_connection_count,
    )

    log.info("Connection established")


async def close_db_connection(app: FastAPI) -> None:
    log.info("Closing connection to database")

    await app.state.pool.close()

    log.info("Connection closed")
