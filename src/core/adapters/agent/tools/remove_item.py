from langchain.messages import ToolMessage
from langchain.tools import tool
from langgraph.types import Command

from core.domain.exceptions import DomainError
from core.domain.value_objects import Amount, LineItemID

from .base import EmptyGoTo, ModifyReceiptRuntime


@tool
def remove_item(
    runtime: ModifyReceiptRuntime, item: LineItemID, amount: Amount
) -> Command[EmptyGoTo]:
    """
    Remove an item from unassigned.
    Example of use: the user says that they did not purchase this item in the first place.
    You can check the LineItemID using show_receipt.
    """
    receipt = runtime.state["receipt"]
    try:
        receipt.remove_item(item, amount)
        message_text = "Successfully updated receipt"
    except DomainError as err:
        message_text = (
            f"Failed to update receipt.\n"
            f"Error type: {type(err).__name__}\n"
            f"Error details: {vars(err)}"
        )
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
