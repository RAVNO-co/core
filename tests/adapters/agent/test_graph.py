from unittest.mock import AsyncMock, Mock

import pytest
from langchain.messages import AIMessage
from langchain.tools import BaseTool
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver

from core.adapters.agent import (
    AgentModelProvider,
    create_agent_graph,
)
from core.adapters.agent.checkpointer import create_inmemory_checkpointer
from core.adapters.agent.context import ReceiptModificationContext
from core.adapters.agent.state import InvokeState


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
