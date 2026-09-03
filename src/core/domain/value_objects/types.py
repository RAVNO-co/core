from enum import StrEnum
from typing import BinaryIO, NewType
from uuid import UUID

UserID = NewType("UserID", UUID)
ReceiptID = NewType("ReceiptID", UUID)
LineItemID = NewType("LineItemID", UUID)

ReceiptTitle = NewType("ReceiptTitle", str)
LineItemName = NewType("LineItemName", str)
UserNickname = NewType("UserNickname", str)

MessageText = NewType("MessageText", str)
Photo = NewType("Photo", BinaryIO)
Audio = NewType("Audio", BinaryIO)


class AssignmentKind(StrEnum):
    CONSUMER = "consumer"
    PAYER = "payer"
