from dishka import Provider, Scope, provide
from langchain.tools import BaseTool
from langchain_openrouter import ChatOpenRouter
from langgraph.pregel.main import BaseCheckpointSaver
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from src.core.adapters.agent import (
    Agent,
    AgentGraph,
    AgentModelProvider,
    create_agent_graph,
)
from src.core.adapters.agent.checkpointer import (
    construct_memory_checkpointer,
    construct_postgres_checkpointer,
)
from src.core.adapters.agent.context import create_context
from src.core.adapters.agent.state import (
    create_invoke_state,
)
from src.core.adapters.agent.tools import (
    create_append_item_tool,
    create_assign_consumption_tool,
    create_assign_payment_tool,
    create_remove_item_tool,
    create_show_receipt_tool,
    create_unassign_consumption_tool,
    create_unassign_payment_tool,
)
from src.core.application.common.agent import AgentI
from src.core.domain.services import CreateLineItem
from src.core.settings import (
    AgentCheckpointerSettings,
    AgentSettings,
    BaseSettings,
)


class AgentProvider(Provider):
    scope = Scope.APP

    @provide
    @staticmethod
    def get_agent(
        graph: AgentGraph,
    ) -> AgentI:
        return Agent(
            state_factory=create_invoke_state,
            context_factory=create_context,
            graph=graph,
        )

    @provide
    @staticmethod
    def get_agent_graph(
        model_provider: AgentModelProvider,
        checkpointer: BaseCheckpointSaver[str],
        tools: tuple[BaseTool, ...],
    ) -> AgentGraph:
        return create_agent_graph(model_provider, checkpointer, tools)

    @provide
    @staticmethod
    def get_model_provider(
        base_settings: BaseSettings, agent_settings: AgentSettings
    ) -> AgentModelProvider:
        return AgentModelProvider(
            ChatOpenRouter(
                api_key=base_settings.OPENROUTER_API_KEY,
                model=agent_settings.AGENT_MODEL,
                temperature=agent_settings.TEMPERATURE,
                max_tokens=agent_settings.MAX_TOKENS,
                reasoning=agent_settings.REASONING,
            )
        )

    @provide
    @staticmethod
    async def get_checkpointer(
        settings: AgentSettings,
    ) -> BaseCheckpointSaver[str]:
        if settings.CHECKPOINTER_DSN is None:
            return construct_memory_checkpointer()

        pool = AsyncConnectionPool(
            str(settings.CHECKPOINTER_DSN),
            kwargs={"autocommit": True, "row_factory": dict_row},
        )

        checkpointer = construct_postgres_checkpointer(pool)  # type: ignore[arg-type]
        await checkpointer.setup()
        return checkpointer

    @provide
    @staticmethod
    def get_tools(
        create_line_item_service: CreateLineItem,
    ) -> tuple[BaseTool, ...]:
        return (
            create_append_item_tool(create_line_item_service),
            create_assign_consumption_tool(),
            create_assign_payment_tool(),
            create_remove_item_tool(),
            create_show_receipt_tool(),
            create_unassign_consumption_tool(),
            create_unassign_payment_tool(),
        )
