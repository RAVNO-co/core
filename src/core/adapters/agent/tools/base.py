from typing import Protocol

from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime
from langgraph.types import Command

from core.adapters.agent.context import ReceiptModificationContext
from core.adapters.agent.state import ReceiptModificationState
from core.domain.exceptions import DomainError
from core.domain.models import Receipt

EmptyGoTo = tuple[()]

ModifyReceiptRuntime = ToolRuntime[
    ReceiptModificationContext, ReceiptModificationState
]


class ReceiptOperation(Protocol):
    def __call__(self, receipt: Receipt) -> Receipt: ...


def _construct_error_message(err: DomainError) -> str:
    match type(err):
        case _:
            return (
                "Failed to update receipt.\n"
                f"Error type: {type(err).__name__}\n"
                f"Error details: {vars(err)}"
            )


def update_receipt_command_strategy(
    runtime: ModifyReceiptRuntime,
    operation: ReceiptOperation,
) -> Command[EmptyGoTo]:
    """Strategy pattern type shit description"""

    receipt = runtime.state["receipt"]
    message_text = "Successfully updated receipt"

    try:
        receipt = operation(receipt)
    except DomainError as err:
        message_text = _construct_error_message(err)

    return Command(
        update={
            "receipt": receipt,
            "messages": [
                ToolMessage(
                    message_text,
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )
