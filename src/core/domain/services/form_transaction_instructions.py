from collections import defaultdict
from collections.abc import Generator
from decimal import Decimal

from core.domain.exceptions import ReceiptNotFullyFilledError
from core.domain.models import Receipt
from core.domain.services.form_settlement_tables import (
    FormConsumptionTable,
    FormPaymentTable,
)
from core.domain.value_objects import (
    ConsumptionTable,
    Money,
    PaymentTable,
    UserID,
)
from core.domain.value_objects.settlement import TransactionInstructions


class FormTransactionInstructions:
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

        payment_generator = summarize_settlement(FormPaymentTable()(receipt))
        debt_generator = summarize_settlement(FormConsumptionTable()(receipt))

        debtor_id, debt = next(debt_generator)
        for payer_id, total_payed in payment_generator:
            to_return = total_payed

            while to_return > 0:
                returned = min(to_return, debt)
                instructions[debtor_id][payer_id] = Money(returned)

                to_return -= returned
                debt -= returned

                if debt == 0 and to_return != 0:
                    debtor_id, debt = next(debt_generator)

        return instructions
