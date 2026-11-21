from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest
from langchain.messages import HumanMessage

from core.adapters.agent import (
    Agent,
    AgentGraph,
    create_context,
    create_invoke_state,
)
from core.adapters.agent.config import (
    RunnableConfigFactory,
    create_runable_config,
)
from core.adapters.agent.context import ContextFactory
from core.adapters.agent.state import InvokeStateFactory
from core.application.common.agent import HumanRequest
from core.domain.models import Receipt


@pytest.fixture
def graph() -> AgentGraph:
    mock = Mock()
    mock.ainvoke = AsyncMock()
    return mock


@pytest.fixture
def state_factory() -> InvokeStateFactory:
    return create_invoke_state


@pytest.fixture
def context_factory() -> ContextFactory:
    return create_context


@pytest.fixture
def config_factory() -> RunnableConfigFactory:
    return create_runable_config


async def test_agent(
    receipt: Receipt,
    human_request: HumanRequest,
    graph: AgentGraph,
    state_factory: InvokeStateFactory,
    context_factory: ContextFactory,
    config_factory: RunnableConfigFactory,
) -> None:
    agent = Agent(
        graph=graph,
        state_factory=state_factory,
        context_factory=context_factory,
        config_factory=config_factory,
    )

    await agent.invoke(human_request)

    graph = cast(Mock, graph)
    call_args = graph.ainvoke.await_args
    assert call_args.kwargs["input"]["receipt"] == receipt
    assert len(call_args.kwargs["input"]["messages"]) == 1
    assert isinstance(call_args.kwargs["input"]["messages"][0], HumanMessage)
