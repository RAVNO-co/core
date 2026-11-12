from langchain.tools import BaseTool, tool
from langgraph.types import Command

from core.domain.models import Receipt
from core.domain.value_objects import Amount, LineItemID, UserID

from .base import (
    EmptyGoTo,
    ModifyReceiptRuntime,
    update_receipt_command_strategy,
)


def create_unassign_consumption_tool() -> BaseTool:
    @tool
    def unassign_consumption(
        runtime: ModifyReceiptRuntime,
        item: LineItemID,
        user_id: UserID,
        amount: Amount,
    ) -> Command[EmptyGoTo]:
        """
        Remove an item assigned as consumed for a user.
        To find out the UserID and LineItemID, you can use show_receipt.
        """

        def unassign_item_operation(receipt: Receipt) -> Receipt:
            receipt.unassign_consumption(item, user_id, amount)
            return receipt

        return update_receipt_command_strategy(
            runtime, unassign_item_operation
        )

    return unassign_consumption
