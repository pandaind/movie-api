from sqlalchemy.ext.asyncio import AsyncSession
from app.models.credit_card import CreditCard
from app.security.security import encrypt_credit_card_info, decrypt_credit_card_info

class CreditCardService:
    @staticmethod
    async def create_credit_card(session: AsyncSession, card_info: dict) -> CreditCard:
        encrypted_card_info = {
            "number": encrypt_credit_card_info(card_info["number"]),
            "expiration_date": encrypt_credit_card_info(card_info["expiration_date"]),
            "cvv": encrypt_credit_card_info(card_info["cvv"]),
            "card_holder_name": encrypt_credit_card_info(card_info["card_holder_name"]),
        }
        credit_card = CreditCard(**encrypted_card_info)
        session.add(credit_card)
        await session.commit()
        await session.refresh(credit_card)
        return credit_card

    @staticmethod
    async def get_credit_card(session: AsyncSession, card_id: int) -> CreditCard | None:
        credit_card = await session.get(CreditCard, card_id)
        if credit_card:
            credit_card.number = decrypt_credit_card_info(credit_card.number)
            credit_card.expiration_date = decrypt_credit_card_info(credit_card.expiration_date)
            credit_card.cvv = decrypt_credit_card_info(credit_card.cvv)
            credit_card.card_holder_name = decrypt_credit_card_info(credit_card.card_holder_name)
        return credit_card

    @staticmethod
    async def update_credit_card(session: AsyncSession, card_id: int, card_info: dict) -> CreditCard | None:
        credit_card = await session.get(CreditCard, card_id)
        if credit_card:
            for key, value in card_info.items():
                setattr(credit_card, key, encrypt_credit_card_info(value))
            await session.commit()
            await session.refresh(credit_card)
        return credit_card

    @staticmethod
    async def delete_credit_card(session: AsyncSession, card_id: int) -> bool:
        credit_card = await session.get(CreditCard, card_id)
        if credit_card:
            await session.delete(credit_card)
            await session.commit()
            return True
        return False