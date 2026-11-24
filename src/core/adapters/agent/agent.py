from core.adapters.agent.config import RunnableConfigFactory
from core.adapters.agent.graph import AgentGraph
from core.application.common.agent import (
    AgentI,
    AgentMessage,
    AgentResponse,
    HumanRequest,
)

from .context import ContextFactory
from .state import InvokeStateFactory


class Agent(AgentI):
    def __init__(
        self,
        graph: AgentGraph,
        state_factory: InvokeStateFactory,
        context_factory: ContextFactory,
        config_factory: RunnableConfigFactory,
    ) -> None:
        self.graph = graph
        self.create_state = state_factory
        self.create_context = context_factory
        self.create_config = config_factory

    async def invoke(self, request: HumanRequest) -> AgentResponse:
        answer = await self.graph.ainvoke(
            input=self.create_state(request),
            context=self.create_context(request),
            config=self.create_config(request),
        )

        return AgentResponse(
            answer=AgentMessage(answer["messages"][-1].content),
            updated_receipt=answer["receipt"],
            updated_participants=answer["participants"],
        )
