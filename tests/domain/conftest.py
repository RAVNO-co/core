import pytest

from core.domain.services import (
    CreateDummyUser,
    CreateLineItem,
    CreateRealUser,
    CreateReceipt,
    FormConsumptionTable,
    FormPaymentTable,
    FormTransactionInstructions,
)


@pytest.fixture
def create_dummy_user() -> CreateDummyUser:
    return CreateDummyUser()


@pytest.fixture
def create_real_user() -> CreateRealUser:
    return CreateRealUser()


@pytest.fixture
def create_line_item() -> CreateLineItem:
    return CreateLineItem()


@pytest.fixture
def create_receipt() -> CreateReceipt:
    return CreateReceipt()


@pytest.fixture
def form_consumption_table() -> FormConsumptionTable:
    return FormConsumptionTable()


@pytest.fixture
def form_payment_table() -> FormPaymentTable:
    return FormPaymentTable()


@pytest.fixture
def form_transaction_instructions(
    form_payment_table: FormPaymentTable,
    form_consumption_table: FormConsumptionTable,
) -> FormTransactionInstructions:
    return FormTransactionInstructions(
        form_consumption_table, form_payment_table
    )
