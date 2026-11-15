from collections.abc import AsyncGenerator

import pytest_asyncio
from dishka import AsyncContainer

from core.di import container as app_container


@pytest_asyncio.fixture
async def container() -> AsyncGenerator[AsyncContainer]:
    async with app_container() as request_container:
        yield request_container
    await app_container.close()
