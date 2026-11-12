from langchain.tools import BaseTool, tool
from langgraph.types import Command

from core.domain.models import Receipt
from core.domain.value_objects import Amount, LineItemID, UserID

from .base import (
    EmptyGoTo,
    ModifyReceiptRuntime,
    update_receipt_command_strategy,
)


def create_unassign_payment_tool() -> BaseTool:
    @tool
    def unassign_payment(
        runtime: ModifyReceiptRuntime,
        item: LineItemID,
        user_id: UserID,
        amount: Amount,
    ) -> Command[EmptyGoTo]:
        """
        Remove an item assigned as paid for a user.
        To find out the UserID and LineItemID, you can use show_receipt.
        """

        def unassign_payment_operation(receipt: Receipt) -> Receipt:
            receipt.unassign_payment(item, user_id, amount)
            return receipt

        return update_receipt_command_strategy(
            runtime, unassign_payment_operation
        )

    return unassign_payment
