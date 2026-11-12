from re import DOTALL, sub
from typing import NewType

from langgraph.graph.state import CompiledStateGraph

from core.application.common.agent import (
    AgentI,
    AgentMessage,
    AgentResponse,
    HumanRequest,
)

from .context import ContextFactory, ReceiptModificationContext
from .state import InvokeState, InvokeStateFactory, ReceiptModificationState

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
        graph: AgentGraph,
        state_factory: InvokeStateFactory,
        context_factory: ContextFactory,
    ) -> None:
        self.graph = graph
        self.create_state = state_factory
        self.create_context = context_factory

    async def invoke(self, request: HumanRequest) -> AgentResponse:
        answer = await self.graph.ainvoke(
            input=self.create_state(request),
            context=self.create_context(request.user_id),
        )

        return AgentResponse(
            answer=AgentMessage(
                self._md_to_html(answer["messages"][-1].content)
            ),
            updated_receipt=answer["receipt"],
            updated_participants=answer["participants"],
        )

    def _refactor_response(self, text: str) -> str:
        return sub(
            r"\s*<think>.*?</think>\s*",
            "🤔",
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
