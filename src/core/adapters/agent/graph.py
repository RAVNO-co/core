from langchain_core.tools import BaseTool

from langchain_openrouter import ChatOpenRouter
from typing import Literal, NewType
from langgraph.checkpoint.base import BaseCheckpointSaver
from re import DOTALL, sub
from typing import TYPE_CHECKING, Literal, NewType
import uuid
from langchain.messages import (
    AIMessage,
    HumanMessage,
    ToolMessage,
    SystemMessage,
)
from langchain_core.messages import BaseMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

from core.application.common.agent import (
    AgentI,
    AgentMessage,
    AgentResponse,
    HumanRequest,
)
from core.domain.services import (
    CreateDummyUser,
    CreateRealUser,
    CreateReceipt,
)
from core.adapters.agent.tools import (
    append_item,
    assign_consumption,
    assign_payment,
    format_receipt,
    remove_item,
    show_receipt,
    unassign_consumption,
    unassign_payment,
)
from .context import ReceiptModificationContext
from .state import InvokeState, ReceiptModificationState
from .templating import system_prompt_template, user_prompt_template

if TYPE_CHECKING:
    from core.domain.models import Receipt, User


AgentModelClient = NewType("AgentModelClient", ChatOpenRouter)


def create_agent_graph(
    client: AgentModelClient,
    checkpointer: BaseCheckpointSaver[str],
    tools: list[BaseTool],
) -> CompiledStateGraph[
    ReceiptModificationState,
    ReceiptModificationContext,
    InvokeState,
    ReceiptModificationState,
]:

    def request_receipt(
        state: ReceiptModificationState,
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

    async def llm_call(
        state: ReceiptModificationState,
    ) -> dict[str, list[BaseMessage]]:
        messages: list[BaseMessage] = [
            SystemMessage(content=system_prompt_template.render()),
            *state["messages"],
        ]

        return {"messages": [await llm_with_tools.ainvoke(messages)]}

    def should_continue(
        state: ReceiptModificationState,
    ) -> Literal["tool_node", "__end__"]:
        messages = state["messages"]
        last_message = messages[-1]

        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "tool_node"

        return "__end__"

    llm_with_tools = client.bind_tools(tools)

    agent_builder = StateGraph[
        ReceiptModificationState,
        ReceiptModificationContext,
        InvokeState,
        ReceiptModificationState,
    ](
        state_schema=ReceiptModificationState,
        context_schema=ReceiptModificationContext,
        input_schema=InvokeState,
    )

    agent_builder.add_node("request_receipt", request_receipt)
    agent_builder.add_node("tool_node", ToolNode(tools))
    agent_builder.add_node("llm_call", llm_call)

    agent_builder.add_edge(START, "request_receipt")
    agent_builder.add_edge("request_receipt", "tool_node")
    agent_builder.add_edge("tool_node", "llm_call")
    agent_builder.add_conditional_edges(
        "llm_call", should_continue, ["tool_node", END]
    )
    return agent_builder.compile(checkpointer=checkpointer)
