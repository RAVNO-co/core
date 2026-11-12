from langchain.tools import BaseTool, tool
from langgraph.types import Command

from core.domain.models import Receipt
from core.domain.value_objects import Amount, LineItemID

from .base import (
    EmptyGoTo,
    ModifyReceiptRuntime,
    update_receipt_command_strategy,
)


def create_remove_item_tool() -> BaseTool:
    @tool
    def remove_item(
        runtime: ModifyReceiptRuntime, item: LineItemID, amount: Amount
    ) -> Command[EmptyGoTo]:
        """
        Remove an item from unassigned.
        Example of use: the user says that they did not purchase this item in\
         the first place.
        You can check the LineItemID using show_receipt.
        """

        def remove_item_operation(receipt: Receipt) -> Receipt:
            receipt.remove_item(item, amount)
            return receipt

        return update_receipt_command_strategy(runtime, remove_item_operation)

    return remove_item
