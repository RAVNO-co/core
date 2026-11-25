from core.application.common.agent import (
    AgentI,
    AgentResponse,
    HumanRequest,
)
from core.application.common.observability import AgentTraceContextFactory


class TracedAgent(AgentI):
    def __init__(
        self,
        agent: AgentI,
        trace_context_factory: AgentTraceContextFactory,
    ) -> None:
        self.agent = agent
        self.trace_context_factory = trace_context_factory

    async def invoke(self, request: HumanRequest) -> AgentResponse:
        with self.trace_context_factory(request):
            return await self.agent.invoke(request)
