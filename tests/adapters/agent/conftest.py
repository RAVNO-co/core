from random import randint
from unittest.mock import Mock

import pytest
from langchain_core.runnables import RunnableConfig
from mimesis import Text

from core.adapters.agent import create_context, create_invoke_state
from core.adapters.agent.config import create_runable_config
from core.adapters.agent.context import ReceiptModificationContext
from core.adapters.agent.state import InvokeState, ReceiptModificationState
from core.adapters.agent.tools.base import ModifyReceiptRuntime
from core.application.common.agent import HumanRequest
from core.application.common.asr import SpeechText
from core.application.common.ocr import ImageText
from core.domain.models import Receipt
from core.domain.value_objects import MessageText
from tests.mocks import RealUserFactory


@pytest.fixture
def human_request(
    receipt: Receipt, real_user_factory: RealUserFactory
) -> HumanRequest:
    text_provider = Text()
    return HumanRequest(
        user_id=next(iter(receipt.participant_ids)),
        message_text=MessageText(text_provider.text()),
        transcribed_audios=tuple(
            SpeechText(text_provider.text()) for _ in range(randint(0, 10))
        ),
        transcribed_photos=tuple(
            ImageText(text_provider.text()) for _ in range(randint(0, 10))
        ),
        receipt=receipt,
        participants=[
            real_user_factory(id=user_id)
            for user_id in receipt.participant_ids
        ],
    )


@pytest.fixture
def invoke_state(human_request: HumanRequest) -> InvokeState:
    return create_invoke_state(human_request)


@pytest.fixture
def context(human_request: HumanRequest) -> ReceiptModificationContext:
    return create_context(human_request)


@pytest.fixture
def config(human_request: HumanRequest) -> RunnableConfig:
    return create_runable_config(human_request)


@pytest.fixture
def tool_runtime(
    # Actually it is InvokeState but they are identical
    invoke_state: ReceiptModificationState,
    context: ReceiptModificationContext,
    config: RunnableConfig,
) -> ModifyReceiptRuntime:
    return ModifyReceiptRuntime(
        state=invoke_state,
        context=context,
        config=config,
        stream_writer=Mock(),
        tool_call_id="receipt-tool-call",
        store=None,
    )
