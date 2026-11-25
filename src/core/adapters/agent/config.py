from typing import Protocol

from langchain_core.runnables import RunnableConfig
from langfuse.langchain import CallbackHandler

from core.application.common.agent import HumanRequest


class RunnableConfigFactory(Protocol):
    def __call__(self, request: HumanRequest) -> RunnableConfig: ...


class LangFuseRunnableConfigFactory:
    def __init__(self, langfuse_handler: CallbackHandler) -> None:
        self._langfuse_handler = langfuse_handler

    def __call__(self, request: HumanRequest) -> RunnableConfig:
        return {
            "configurable": {
                "thread_id": str(request.receipt.id),
            },
            "callbacks": [self._langfuse_handler],
            "run_name": "agent-invoke",
        }


def create_runable_config(request: HumanRequest) -> RunnableConfig:
    return {
        "configurable": {"thread_id": str(request.receipt.id)},
    }
