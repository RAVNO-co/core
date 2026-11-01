from re import DOTALL, sub
from typing import TYPE_CHECKING, Literal, NewType
from langchain_core.tools import BaseTool

from langchain.messages import AIMessage, HumanMessage, SystemMessage
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

AgentGraph = NewType(
    "AgentGraph",
    CompiledStateGraph[
        ReceiptModificationState,
        ReceiptModificationContext,
        InvokeState,
        ReceiptModificationState,
    ],
)


class Agent(AgentI):
    def __init__(
        self,
        real_user_service: CreateRealUser,
        dummy_user_service: CreateDummyUser,
        receipt_service: CreateReceipt,
        graph: AgentGraph,
    ) -> None:
        self.tools: list[BaseTool] = [
            append_item,
            assign_consumption,
            assign_payment,
            remove_item,
            show_receipt,
            unassign_consumption,
            unassign_payment,
        ]
        self.real_user_service = real_user_service
        self.dummy_user_service = dummy_user_service
        self.receipt_service = receipt_service
        self.agent = graph

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

    @staticmethod
    def _construct_invoke_state(
        request: HumanRequest, receipt: Receipt, participants: list[User]
    ) -> InvokeState:
        return {
            "messages": [
                HumanMessage(
                    user_prompt_template.render(
                        user_id=request.user_id,
                        user_input=request.message_text,
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
