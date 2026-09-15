from langchain.messages import ToolMessage
from langchain.tools import tool
from langgraph.types import Command

from core.domain.exceptions import DomainError
from core.domain.value_objects import LineItemID

from .base import EmptyGoTo, ModifyReceiptRuntime


@tool
def remove_item(
    runtime: ModifyReceiptRuntime,
    item: LineItemID,
) -> Command[EmptyGoTo]:
    """
    Удалить товар из неназначенных.

    Пример использования: пользователь говорит,
    что данного товара они изначально не приобретали.

    LineItemID можно посмотреть с помощью show_receipt
    """
    receipt = runtime.state["receipt"]
    try:
        receipt.remove_item(item)
        message_text = "Successfully updated receipt"
    except DomainError as err:
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
