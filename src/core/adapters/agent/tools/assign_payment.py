from langchain.tools import BaseTool, tool
from langgraph.types import Command

from core.domain.models import Receipt
from core.domain.value_objects import Amount, LineItemID, UserID

from .base import (
    EmptyGoTo,
    ModifyReceiptRuntime,
    update_receipt_command_strategy,
)


def create_assign_payment_tool() -> BaseTool:
    @tool
    def assign_payment(
        runtime: ModifyReceiptRuntime,
        item: LineItemID,
        user_id: UserID,
        amount: Amount,
    ) -> Command[EmptyGoTo]:
        """
        Assign a payer to a LineItem.
        You need to specify the UserID of the user who paid for the item,
        the LineItemID of the item, and the quantity of the item paid for by the user.
        To find out the UserID and LineItemID, you can use show_receipt.
        """

        def assign_payment_operation(receipt: Receipt) -> Receipt:
            receipt.assign_payment(item, user_id, amount)
            return receipt

        return update_receipt_command_strategy(
            runtime, assign_payment_operation
        )

    return assign_payment
