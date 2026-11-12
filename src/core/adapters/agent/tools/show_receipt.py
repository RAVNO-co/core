from langchain.messages import ToolMessage
from langchain.tools import BaseTool, tool
from langgraph.types import Command

from core.adapters.agent.templating import (
    show_receipt_tool_prompt_template,
)

from .base import EmptyGoTo, ModifyReceiptRuntime


def create_show_receipt_tool() -> BaseTool:
    @tool
    def show_receipt(runtime: ModifyReceiptRuntime) -> Command[EmptyGoTo]:
        """
        Get the current status of the receipt.
        - Current user
        - User list
        - Unassigned items
        - Item assignments
        """

        text = show_receipt_tool_prompt_template.render(
            current_user_id=runtime.context["current_user_id"],
            user_id_mapping=runtime.state["participants"],
            items=runtime.state["receipt"],
        )
        message = ToolMessage(
            text,
            tool_call_id=runtime.tool_call_id,
        )

        return Command(
            update={
                "messages": [message],
            }
        )

    return show_receipt
