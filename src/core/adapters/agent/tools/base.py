from langchain.tools import ToolRuntime
from src.core.adapters.agent.context import ReceiptModificationContext
from src.core.adapters.agent.state import ReceiptModificationState

EmptyGoTo = tuple[()]

ModifyReceiptRuntime = ToolRuntime[
    ReceiptModificationContext, ReceiptModificationState
]
