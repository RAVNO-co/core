from datetime import UTC, datetime
from uuid import uuid7

from core.domain.models import RealUser, Receipt
from core.domain.value_objects import ReceiptID, ReceiptTitle


class CreateReceipt:
    def __call__(self, author: RealUser, title: ReceiptTitle) -> Receipt:
        return Receipt(
            id=ReceiptID(uuid7()),
            title=title,
            author_id=author.id,
            created_at=datetime.now(UTC),
            participant_ids={author.id},
        )
