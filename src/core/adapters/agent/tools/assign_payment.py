from langchain.messages import ToolMessage
from langchain.tools import tool
from langgraph.types import Command

from core.domain.exceptions import DomainError
from core.domain.value_objects import Amount, LineItemID, UserID

from .base import EmptyGoTo, ModifyReceiptRuntime


@tool
def assign_payment(
    runtime: ModifyReceiptRuntime,
    item: LineItemID,
    user_id: UserID,
    amount: Amount,
) -> Command[EmptyGoTo]:
    """
    Назначить для LineItem оплатившего.
    Тебе необходимо указать UserID пользователя оплатившего товар,
    LineItemID товара и количество оплаченного пользователем товара.
    Чтобы узнать UserID и LineItemID ты можешь воспользоваться show_receipt
    """
    receipt = runtime.state["receipt"]
    try:
        receipt.assign_payment(item, user_id, amount)
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
