from typing import Annotated, Any, Protocol, Required, TypedDict

from langchain.agents import AgentState
from langchain.messages import AnyMessage, HumanMessage
from langgraph.graph.message import add_messages

from core.adapters.agent.templating import user_prompt_template
from core.application.common.agent import HumanRequest
from core.domain.models import Receipt, User

NoStructuredResponse = type(None)


class InvokeState(TypedDict):
    messages: Required[
        Annotated[list[AnyMessage | dict[str, Any]], add_messages]
    ]
    receipt: Required[Receipt]
    participants: Required[list[User]]


class ReceiptModificationState(AgentState[NoStructuredResponse]):
    receipt: Required[Receipt]
    participants: Required[list[User]]


class InvokeStateFactory(Protocol):
    def __call__(self, request: HumanRequest) -> InvokeState: ...


def create_invoke_state(request: HumanRequest) -> InvokeState:
    return {
        "messages": [
            HumanMessage(
                user_prompt_template.render(
                    user_id=request.user_id,
                    user_input=request.message_text,
                    transcribed_photos=request.transcribed_photos,
                    transcribed_audios=request.transcribed_audios,
                )
            ),
        ],
        "receipt": request.receipt,
        "participants": request.participants,
    }
