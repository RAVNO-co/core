from unittest.mock import AsyncMock, Mock

import pytest
from langchain.messages import AIMessage
from langchain.tools import BaseTool
from langgraph.graph.state import RunnableConfig
from langgraph.pregel.main import BaseCheckpointSaver

from core.adapters.agent import (
    AgentModelProvider,
    create_agent_graph,
    create_context,
    create_invoke_state,
)
from core.adapters.agent.checkpointer import create_inmemory_checkpointer
from core.adapters.agent.config import create_runable_config
from core.adapters.agent.context import ReceiptModificationContext
from core.adapters.agent.state import InvokeState
from core.adapters.agent.tools import (
    create_assign_consumption_tool,
)
from core.application.common.agent import HumanRequest


@pytest.fixture
def model_provider() -> AgentModelProvider:
    model = Mock()
    bound_model = model.bind_tools.return_value
    bound_model.ainvoke = AsyncMock()

    bound_model.ainvoke.side_effect = [
        AIMessage(
            "",
            tool_calls=[
                {
                    "name": "append_item",
                    "args": {
                        "name": "Graph test item",
                        "total_amount": "1.5",
                        "price": "3.25",
                    },
                    "id": "append-call",
                }
            ],
        ),
        AIMessage("Done"),
    ]
    return model


@pytest.fixture
def checkpointer() -> BaseCheckpointSaver[str]:
    return create_inmemory_checkpointer()


@pytest.fixture
def tools() -> tuple[BaseTool, ...]:
    return ()


@pytest.fixture
def invoke_state(human_request: HumanRequest) -> InvokeState:
    return create_invoke_state(human_request)


@pytest.fixture
def context(human_request: HumanRequest) -> ReceiptModificationContext:
    return create_context(human_request)


@pytest.fixture
def config(human_request: HumanRequest) -> RunnableConfig:
    return create_runable_config(human_request)


async def test_graph(
    invoke_state: InvokeState,
    context: ReceiptModificationContext,
    config: RunnableConfig,
    model_provider: AgentModelProvider,
    checkpointer: BaseCheckpointSaver[str],
    tools: tuple[BaseTool, ...],
) -> None:
    graph = create_agent_graph(model_provider, checkpointer, tools)

    await graph.ainvoke(invoke_state, config=config, context=context)
