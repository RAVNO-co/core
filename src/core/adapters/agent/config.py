from typing import Protocol

from langgraph.graph.state import RunnableConfig

from core.application.common.agent import HumanRequest


class RunnableConfigFactory(Protocol):
    def __call__(self, request: HumanRequest) -> RunnableConfig: ...


def create_runable_config(request: HumanRequest) -> RunnableConfig:
    return {
        "configurable": {"thread_id": str(request.receipt.id)},
    }
