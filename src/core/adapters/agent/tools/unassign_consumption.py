from langchain.messages import ToolMessage
from langchain.tools import tool
from langgraph.types import Command

from core.domain.exceptions import DomainError
from core.domain.value_objects import Amount, LineItemID, UserID

from .base import EmptyGoTo, ModifyReceiptRuntime


@tool
def unassign_consumption(
    runtime: ModifyReceiptRuntime,
    item: LineItemID,
    user_id: UserID,
    amount: Amount,
) -> Command[EmptyGoTo]:
    """
    Убрать товар из назначенного в качестве потребленного пользователю.
    Чтобы узнать UserID и LineItemID ты можешь воспользоваться show_receipt
    """
    receipt = runtime.state["receipt"]
    try:
        receipt.unassign_consumption(item, user_id, amount)
        message_text = "Successfully updated receipt"
    except (DomainError, KeyError) as err:
        message_text = f"Failed to update receipt: {type(err)} {err!s}"
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
