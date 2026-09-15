from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from psycopg_pool import AsyncConnectionPool

serde = JsonPlusSerializer(
    allowed_msgpack_modules=(
        ("core.domain.models.receipt", "Receipt"),
        ("core.domain.models.user", "RealUser"),
        ("core.domain.models.user", "DummyUser"),
        ("core.domain.value_objects", "LineItem"),
    ),
)


def construct_postgres_checkpointer(
    pool: AsyncConnectionPool[AsyncConnection[DictRow]],
) -> AsyncPostgresSaver:
    return AsyncPostgresSaver(pool, serde=serde)


def construct_memory_checkpointer() -> InMemorySaver:
    return InMemorySaver(serde=serde)
