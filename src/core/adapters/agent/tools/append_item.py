from langchain.messages import ToolMessage
from langchain.tools import tool
from langgraph.types import Command

from core.domain.exceptions import DomainError
from core.domain.services import CreateLineItem
from core.domain.value_objects import (
    Amount,
    LineItemName,
    Money,
)

from .base import EmptyGoTo, ModifyReceiptRuntime

create_line_item = CreateLineItem()


@tool
def append_item(
    runtime: ModifyReceiptRuntime,
    name: LineItemName,
    total_amount: Amount,
    price: Money,
) -> Command[EmptyGoTo]:
    """
    Добавить товар в неназначенные.
    Тебе необходимо указать:
    1. Название товара
    2. Количество товара
    3. Цену товара(берется из чека)
    """
    receipt = runtime.state["receipt"]

    try:
        item = create_line_item(name, total_amount, price)
        receipt.append_item(item)
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
