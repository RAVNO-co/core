from collections import defaultdict
from collections.abc import Generator
from decimal import Decimal

from core.domain.exceptions import ReceiptNotFullyFilledError
from core.domain.models import Receipt
from core.domain.value_objects import (
    ConsumptionTable,
    Money,
    PaymentTable,
    UserID,
)
from core.domain.value_objects.settlement import TransactionInstructions

from .form_settlement_tables import FormConsumptionTable, FormPaymentTable


class FormTransactionInstructions:
    def __init__(
        self,
        form_consumption_table: FormConsumptionTable,
        form_payemnt_table: FormPaymentTable,
    ) -> None:
        self.form_consumption_table = form_consumption_table
        self.form_payemnt_table = form_payemnt_table

    def __call__(self, receipt: Receipt) -> TransactionInstructions:
        if not receipt.is_filled:
            raise ReceiptNotFullyFilledError
        if not receipt.items:
            return {}

        instructions: TransactionInstructions = defaultdict(dict)

        def summarize_settlement(
            table: PaymentTable | ConsumptionTable,
        ) -> Generator[tuple[UserID, Decimal]]:
            return (
                (user_id, Decimal(settlement.total))
                for user_id, settlement in table.items()
                if user_id is not None
            )

        payment_generator = summarize_settlement(
            self.form_payemnt_table(receipt)
        )
        debt_generator = summarize_settlement(
            self.form_consumption_table(receipt)
        )

        debtor_id, debt = next(debt_generator)
        for payer_id, total_paid in payment_generator:
            to_return = total_paid

            while to_return > 0:
                returned = min(to_return, debt)
                instructions[debtor_id][payer_id] = Money(returned)

                to_return -= returned
                debt -= returned

                if debt == 0 and to_return != 0:
                    debtor_id, debt = next(debt_generator)

        return instructions
