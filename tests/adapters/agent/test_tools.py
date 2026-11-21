from typing import cast
from unittest.mock import Mock

import pytest
from langchain.messages import ToolMessage

from core.adapters.agent.tools import (
    create_append_item_tool,
    create_assign_consumption_tool,
    create_assign_payment_tool,
    create_remove_item_tool,
    create_show_receipt_tool,
    create_unassign_consumption_tool,
    create_unassign_payment_tool,
)
from core.adapters.agent.tools.base import ModifyReceiptRuntime
from core.domain.models import LineItem, Receipt
from core.domain.services import CreateLineItem
from core.domain.value_objects import Amount
from tests.mocks import LineItemData, LineItemFactory


@pytest.fixture
def runtime() -> ModifyReceiptRuntime:
    return Mock()


def test_append_item_tool(
    tool_runtime: ModifyReceiptRuntime, line_item_data: LineItemData
) -> None:
    tool = create_append_item_tool(CreateLineItem())
    tool_input = {
        "runtime": tool_runtime,
        "name": line_item_data["name"],
        "total_amount": line_item_data["total_amount"],
        "price": line_item_data["price"],
    }

    command = tool.invoke(tool_input)
    assert isinstance(command.update["messages"][-1], ToolMessage)


def test_remove_item_tool(
    tool_runtime: ModifyReceiptRuntime,
    receipt: Receipt,
    line_item_factory: LineItemFactory,
) -> None:
    tool = create_remove_item_tool()
    line_item = line_item_factory(consumptions={}, payments={})
    receipt.append_item(line_item)
    tool_input = {
        "runtime": tool_runtime,
        "item": line_item.id,
        "amount": line_item.free_amount,
    }

    command = tool.invoke(tool_input)
    assert isinstance(command.update["messages"][-1], ToolMessage)


def test_show_receipt_tool(tool_runtime: ModifyReceiptRuntime) -> None:
    tool = create_show_receipt_tool()
    tool_input = {
        "runtime": tool_runtime,
    }

    command = tool.invoke(tool_input)
    assert isinstance(command.update["messages"][-1], ToolMessage)


def test_assign_payment_tool(
    tool_runtime: ModifyReceiptRuntime, receipt: Receipt, line_item: LineItem
) -> None:
    tool = create_assign_payment_tool()
    receipt.append_item(line_item)
    tool_input = {
        "runtime": tool_runtime,
        "item": line_item.id,
        "amount": line_item.free_amount,
        "user_id": receipt.author_id,
    }

    command = tool.invoke(tool_input)
    assert isinstance(command.update["messages"][-1], ToolMessage)


def test_assign_consumption_tool(
    tool_runtime: ModifyReceiptRuntime, receipt: Receipt, line_item: LineItem
) -> None:
    tool = create_assign_consumption_tool()
    receipt.append_item(line_item)
    tool_input = {
        "runtime": tool_runtime,
        "item": line_item.id,
        "amount": line_item.free_amount,
        "user_id": receipt.author_id,
    }

    command = tool.invoke(tool_input)
    assert isinstance(command.update["messages"][-1], ToolMessage)


def test_unassign_payment_tool(
    tool_runtime: ModifyReceiptRuntime, receipt: Receipt, line_item: LineItem
) -> None:
    tool = create_unassign_payment_tool()
    amount = cast(Amount, line_item.free_amount)
    receipt.append_item(line_item)
    receipt.assign_payment(line_item.id, receipt.author_id, amount)
    tool_input = {
        "runtime": tool_runtime,
        "item": line_item.id,
        "amount": amount,
        "user_id": receipt.author_id,
    }

    command = tool.invoke(tool_input)
    assert isinstance(command.update["messages"][-1], ToolMessage)


def test_unassign_consumption_tool(
    tool_runtime: ModifyReceiptRuntime, receipt: Receipt, line_item: LineItem
) -> None:
    tool = create_unassign_consumption_tool()
    amount = cast(Amount, line_item.free_amount)
    receipt.append_item(line_item)
    receipt.assign_payment(line_item.id, receipt.author_id, amount)
    tool_input = {
        "runtime": tool_runtime,
        "item": line_item.id,
        "amount": line_item.free_amount,
        "user_id": receipt.author_id,
    }

    command = tool.invoke(tool_input)
    assert isinstance(command.update["messages"][-1], ToolMessage)
