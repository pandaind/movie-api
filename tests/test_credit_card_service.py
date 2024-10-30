from unittest.mock import AsyncMock, patch

import pytest

from app.models.credit_card import CreditCard
from app.services.credit_card_service import CreditCardService


@pytest.fixture
def mock_session(mocker):
    session = AsyncMock()
    mocker.patch("app.db.database.get_db", return_value=session)
    return session


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
@pytest.mark.asyncio
async def test_create_credit_card(mock_session):
    card_info = {
        "number": "1234567890123456",
        "expiration_date": "12/25",
        "cvv": "123",
        "card_holder_name": "John Doe",
    }
    encrypted_card_info = {
        "number": "encrypted_1234567890123456",
        "expiration_date": "encrypted_12/25",
        "cvv": "encrypted_123",
        "card_holder_name": "encrypted_John Doe",
    }

    with patch(
        "app.services.credit_card_service.encrypt_credit_card_info",
        side_effect=lambda x: f"encrypted_{x}",
    ):
        credit_card = await CreditCardService.create_credit_card(
            mock_session, card_info
        )

    assert credit_card.number == encrypted_card_info["number"]
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_get_credit_card(mock_session):
    card_id = 1
    credit_card = CreditCard(
        id=card_id,
        number="encrypted_number",
        expiration_date="encrypted_expiration_date",
        cvv="encrypted_cvv",
        card_holder_name="encrypted_card_holder_name",
    )
    mock_session.get.return_value = credit_card

    with patch(
        "app.services.credit_card_service.decrypt_credit_card_info",
        side_effect=lambda x: x.replace("encrypted_", ""),
    ):
        result = await CreditCardService.get_credit_card(mock_session, card_id)

    assert result.number == "number"
    mock_session.get.assert_called_once_with(CreditCard, card_id)


@pytest.mark.asyncio
async def test_update_credit_card(mock_session):
    card_id = 1
    card_info = {
        "number": "6543210987654321",
        "expiration_date": "11/24",
        "cvv": "321",
        "card_holder_name": "Jane Doe",
    }
    credit_card = CreditCard(
        id=card_id,
        number="encrypted_number",
        expiration_date="encrypted_expiration_date",
        cvv="encrypted_cvv",
        card_holder_name="encrypted_card_holder_name",
    )
    mock_session.get.return_value = credit_card

    with patch(
        "app.services.credit_card_service.encrypt_credit_card_info",
        side_effect=lambda x: f"encrypted_{x}",
    ):
        result = await CreditCardService.update_credit_card(
            mock_session, card_id, card_info
        )

    assert result.number == "encrypted_6543210987654321"
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_delete_credit_card(mock_session):
    card_id = 1
    credit_card = CreditCard(id=card_id)
    mock_session.get.return_value = credit_card

    result = await CreditCardService.delete_credit_card(mock_session, card_id)

    assert result is True
    mock_session.delete.assert_called_once_with(credit_card)
    mock_session.commit.assert_called_once()
