import asyncio
import logging
from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import aioredis
import asyncpg
import backoff
import pytest_asyncio
from aiohttp import ClientSession
from aioredis import Redis
from asyncpg import Connection
from pydantic import BaseModel

from .settings import TestSettings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HTTPResponse(BaseModel):
    body: Any
    headers: Dict[str, Any]
    status: int


@pytest_asyncio.fixture(name="settings", scope="session")
def settings_fixture() -> TestSettings:
    return TestSettings()


@pytest_asyncio.fixture(name="event_loop", scope="session")
def event_loop_fixture() -> asyncio.AbstractEventLoop:
    """Create an instance of the default event loop."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(name="redis_client", scope="session")
async def redis_client_fixture(settings: TestSettings) -> Redis:
    redis = aioredis.from_url(
        f"redis://{settings.redis_settings.host}:{settings.redis_settings.port}",
        encoding="utf8",
        decode_responses=True,
    )
    await wait_for_ping(redis, settings)
    yield redis
    await redis.flushdb()
    await redis.close()


# noinspection PyUnusedLocal
@pytest_asyncio.fixture(name="http_client", scope="session")
async def http_client_fixture(settings, redis_client) -> ClientSession:
    """Represents HTTP client fixture.

    Add dependency fixtures `postgres_client` and `redis_client` to
    check they are ready to work.
    """
    async with ClientSession(base_url=settings.test_url) as session:
        yield session


@pytest_asyncio.fixture(name="make_request", scope="session")
def make_request_fixture(http_client: ClientSession):
    """Make HTTP-request"""

    async def inner(
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        jwt: Optional[str] = None,
    ) -> HTTPResponse:
        params = params or {}
        json = json or {}
        headers = {}

        if jwt:
            headers = {"Authorization": "Bearer {}".format(jwt)}

        logger.debug("URL: %s", url)

        async with http_client.request(
            method, url, params=params, json=json, headers=headers
        ) as response:
            body = await response.json()
            logger.warning("Response: %s", body)

            return HTTPResponse(
                body=body,
                headers=dict(response.headers),
                status=response.status,
            )

    return inner


@pytest_asyncio.fixture(name="postgres_client", scope="session")
async def postgres_client_fixture(settings: TestSettings):
    conn = await asyncpg.connect(
        user=settings.postgres_settings.username,
        password=settings.postgres_settings.password,
        host=settings.postgres_settings.host,
        port=settings.postgres_settings.port,
    )
    yield conn
    await conn.execute("DROP DATABASE  %s", settings.postgres_settings.database_name)
    await conn.close()


@pytest_asyncio.fixture(name="superadmin_token", scope="session")
async def superadmin_token_fixture(make_request):
    superadmin_data = {"login": "superuser", "password": "superpassword"}
    response = await make_request(
        method="POST",
        url="/api/v1/auth/login",
        json=superadmin_data,
    )
    assert response.status == HTTPStatus.OK
    access_token = response.body["access_token"]
    yield access_token
    await make_request(
        method="POST",
        url="/api/v1/auth/logout",
        jwt=access_token,
    )


async def wait_for_ping(client: Union[Redis, Connection], settings: TestSettings):
    """Wait for service client to answer"""
    client_name = type(client).__name__

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=(RuntimeError, ConnectionError, TimeoutError),
        max_time=settings.ping_backoff_timeout,
    )
    async def _ping(inner_client):
        result = await inner_client.ping()
        if not result:
            raise RuntimeError(f"{client_name} still not ready...")

    return await _ping(client)
