from typing import Protocol, cast

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.runnables import RunnableConfig
from langfuse.langchain import CallbackHandler as LangfuseCallback

from core.application.common.agent import HumanRequest


class RunnableConfigFactory(Protocol):
    def __call__(self, request: HumanRequest) -> RunnableConfig: ...


class CreateRunnableConfig(RunnableConfigFactory):
    def __init__(self) -> None:
        self.callbacks = cast(
            list[BaseCallbackHandler],
            [LangfuseCallback()],
        )

    def __call__(self, request: HumanRequest) -> RunnableConfig:
        return {
            "configurable": {
                "thread_id": str(request.receipt.id),
            },
            "callbacks": self.callbacks,
            "run_name": "agent-invoke",
        }
