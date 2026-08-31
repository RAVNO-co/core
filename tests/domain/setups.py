from copy import deepcopy

from core.domain.models import Receipt


def fulfill_receipt(receipt: Receipt) -> Receipt:
    receipt = deepcopy(receipt)

    user_id = next(iter(receipt.participant_ids))
    for item in receipt.items:
        free_payments = item.total_amount - sum(item.payments.values())
        receipt.assign_payment(item.id, user_id, free_payments)

        free_consumptions = item.total_amount - sum(item.consumptions.values())
        receipt.assign_consumption(item.id, user_id, free_consumptions)

    return receipt
