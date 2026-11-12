from langchain.tools import BaseTool, tool
from langgraph.types import Command

from core.domain.models import Receipt
from core.domain.services import CreateLineItem
from core.domain.value_objects import (
    Amount,
    LineItemName,
    Money,
)

from .base import (
    EmptyGoTo,
    ModifyReceiptRuntime,
    update_receipt_command_strategy,
)


def create_append_item_tool(create_line_item: CreateLineItem) -> BaseTool:
    @tool
    def append_item(
        runtime: ModifyReceiptRuntime,
        name: LineItemName,
        total_amount: Amount,
        price: Money,
    ) -> Command[EmptyGoTo]:
        """
        Add an item to unassigned.
        You need to specify:
        1. Item name
        2. Item quantity
        3. Item price (taken from the receipt)
        """

        def append_item_operation(receipt: Receipt) -> Receipt:
            item = create_line_item(name, total_amount, price)
            receipt.append_item(item)
            return receipt

        return update_receipt_command_strategy(runtime, append_item_operation)

    return append_item
