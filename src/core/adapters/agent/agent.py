from re import DOTALL, sub
from typing import TYPE_CHECKING, NewType

from langchain.messages import HumanMessage
from langchain_openrouter import ChatOpenRouter
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import MessagesState
from langchain.messages import SystemMessage
from langgraph.prebuilt import ToolNode

from src.adapters.agent.tools import (
    append_item,
    assign_item,
    remove_item,
    show_receipt,
    format_receipt,
    unassign_item,
)
from src.application.common.agent import AgentI, AgentResponse, HumanRequest
from src.domain.services import ReceiptService, UserService
from src.domain.value_objects import AgentMessage

from .context import ReceiptModificationContext
from .state import InvokeState, ReceiptModificationState
from .templating import system_prompt_template, user_prompt_template

if TYPE_CHECKING:
    from typing import Any

    from src.domain.models import Receipt, User


AgentModelClient = NewType("AgentModelClient", ChatOpenRouter)


class Agent(AgentI):
    def __init__(
        self,
        client: AgentModelClient,
        checkpointer: BaseCheckpointSaver[str],
        user_service: UserService,
        receipt_service: ReceiptService,
    ) -> None:
        self.user_service = user_service
        self.receipt_service = receipt_service
        self.tools=[
                append_item,
                assign_item,
                remove_item,
                show_receipt,
                unassign_item,
            ]
        self.llm_with_tools = client.bind_tools(self.tools)
        self.checkpointer = checkpointer
        self.agent = self._agent_compile()
    

    async def invoke(
        self, request: HumanRequest, receipt: Receipt, participants: list[User]
    ) -> AgentResponse:
        answer = await self.agent.ainvoke(
            input=self._construct_invoke_state(request, receipt, participants),
            config={
                "configurable": {"thread_id": str(receipt.id)},
                "max_concurrency": 1,
            },
            context=self._construct_invoke_context(participants),
        )

        return AgentResponse(
            answer=AgentMessage(
                self._refactor_response(answer["messages"][-1].content)
            ),
            updated_receipt=answer["receipt"],
        )

    def _llm_call(self, state: ReceiptModificationState) -> dict:
        return {
            "messages": [
                await self.llm_with_tools.ainvoke(
                    [
                        SystemMessage(
                            content=system_prompt_template.render()
                        )
                    ]
                    + state["messages"]
                )
            ]
        }

    def _show_receipt_node(
        self,
        state: ReceiptModificationState,
    ):
        text = format_receipt(
            receipt=state["receipt"],
            current_user_id=state["current_user_id"],
            user_id_mapping={
                user.id: user
                for user in state["users"]
            },
        )

        return {
            "messages": [
                SystemMessage(
                    content=(
                        text
                    ),
                )
            ],
        }
    
    def _should_continue(self, state: ReceiptModificationState) -> str:
        messages = state["messages"]
        last_message = messages[-1]

        if last_message.tool_calls:
            return "tool_node"

        return END
    
    def _agent_compile(self):
        agent_builder = StateGraph(ReceiptModificationState)
        agent_builder.add_node("show_receipt", self._show_receipt_node)
        agent_builder.add_node("llm_call", self.llm_call)
        agent_builder.add_node("tool_node", ToolNode(self.tools))
        agent_builder.add_edge(START, "show_receipt")
        agent_builder.add_edge("show_receipt", "llm_call")
        agent_builder.add_conditional_edges(
            "llm_call",
            self._should_continue,
            ["tool_node", END]
        )
        agent_builder.add_edge("tool_node", "llm_call")
        return agent_builder.compile(checkpointer=self.checkpointer)
        
    @staticmethod
    def _construct_invoke_state(
        request: HumanRequest, receipt: Receipt, participants: list[User]
    ) -> InvokeState:
        return {
            "messages": [
                HumanMessage(
                    user_prompt_template.render(
                        user_id=request.user_id,
                        user_input=request.users_input,
                        transcribed_photos=request.transcribed_photos,
                        transcribed_audios=request.transcribed_audios,
                    )
                ),
            ],
            "current_user_id": request.user_id,
            "receipt": receipt,
            "users": participants,
        }

    @staticmethod
    def _construct_invoke_context(
        participants: list[User],
    ) -> ReceiptModificationContext:
        return {"user_id_mapping": {user.id: user for user in participants}}

    def _refactor_response(self, text: str) -> str:
        return sub(
            r"\s*<think>.*?</think>\s*",
            "\n",
            self._md_to_html(text),
            flags=DOTALL,
        ).strip()

    @staticmethod
    def _md_to_html(text: str) -> str:
        """
        Converts markdown tags to HTML
        """
        result = []
        i = 0
        opened = False

        while i < len(text):
            if text[i : i + 2] == "**":
                result.append("</b>" if opened else "<b>")
                opened = not opened
                i += 2
            else:
                result.append(text[i])
                i += 1

        return "".join(result)