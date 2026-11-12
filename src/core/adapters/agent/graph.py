from typing import TYPE_CHECKING, Literal
from uuid import uuid4

from langchain.messages import (
    AIMessage,
    SystemMessage,
)
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool
from langchain_openrouter import ChatOpenRouter
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

from .context import ReceiptModificationContext
from .state import InvokeState, ReceiptModificationState
from .templating import system_prompt_template

if TYPE_CHECKING:
    pass


AgentGraph = CompiledStateGraph[
    ReceiptModificationState,
    ReceiptModificationContext,
    InvokeState,
    ReceiptModificationState,
]


def request_receipt(
    state: ReceiptModificationState,  # ruff: ignore[unused-function-argument]
) -> dict[str, list[AIMessage]]:
    return {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "show_receipt",
                        "args": {},
                        "id": uuid4().hex,
                        "type": "tool_call",
                    }
                ],
            )
        ]
    }


def should_continue(
    state: ReceiptModificationState,
) -> Literal["tool_node", "__end__"]:
    messages = state["messages"]
    last_message = messages[-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tool_node"

    return "__end__"


def create_agent_graph(
    model_provider: ChatOpenRouter,
    checkpointer: BaseCheckpointSaver[str],
    tools: list[BaseTool],
) -> AgentGraph:

    model_with_tools = model_provider.bind_tools(
        tools, parallel_tool_calls=False
    )

    async def llm_call(
        state: ReceiptModificationState,
    ) -> dict[str, list[BaseMessage]]:
        messages: list[BaseMessage] = [
            SystemMessage(content=system_prompt_template.render()),
            *state["messages"],
        ]

        return {"messages": [await model_with_tools.ainvoke(messages)]}

    graph = StateGraph[
        ReceiptModificationState,
        ReceiptModificationContext,
        InvokeState,
        ReceiptModificationState,
    ](
        state_schema=ReceiptModificationState,
        context_schema=ReceiptModificationContext,
        input_schema=InvokeState,
    )

    graph.add_node("request_receipt", request_receipt)
    graph.add_node("tool_node", ToolNode(tools))
    graph.add_node("llm_call", llm_call)

    graph.add_edge(START, "request_receipt")
    graph.add_edge("request_receipt", "tool_node")
    graph.add_edge("tool_node", "llm_call")
    graph.add_conditional_edges(
        "llm_call", should_continue, ["tool_node", END]
    )
    return graph.compile(checkpointer=checkpointer)
