from langchain.tools import ToolRuntime

from core.adapters.agent.context import ReceiptModificationContext
from core.adapters.agent.state import ReceiptModificationState

EmptyGoTo = tuple[()]

ModifyReceiptRuntime = ToolRuntime[
    ReceiptModificationContext, ReceiptModificationState
]
