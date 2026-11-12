from core.domain.exceptions import AccessDeniedError
from core.domain.models import Receipt
from core.domain.value_objects import UserID


class EnsureAccess:
    def __call__(self, receipt: Receipt, user_id: UserID) -> None:
        """Ensure user is receipt participant

        Raises:
            AccessDeniedError: User cant access this receipt
        """
        if user_id not in receipt.participant_ids:
            raise AccessDeniedError
