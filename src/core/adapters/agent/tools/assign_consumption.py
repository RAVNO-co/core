from langchain.messages import ToolMessage
from langchain.tools import tool
from langgraph.types import Command

from core.domain.exceptions import DomainError
from core.domain.value_objects import Amount, LineItemID, UserID

from .base import EmptyGoTo, ModifyReceiptRuntime


@tool
def assign_consumption(
    runtime: ModifyReceiptRuntime,
    item: LineItemID,
    user_id: UserID,
    amount: Amount,
) -> Command[EmptyGoTo]:
    """
    Assign a consumer to a LineItem.
    You need to specify the UserID of the user who consumed the item,
    the LineItemID of the item, and the quantity of the item consumed by the user.
    To find out the UserID and LineItemID, you can use show_receipt.
    """
    receipt = runtime.state["receipt"]
    try:
        receipt.assign_consumption(item, user_id, amount)
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
