from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class CreditCard(Base):
    __tablename__ = "credit_cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str]
    expiration_date: Mapped[str]
    cvv: Mapped[str]
    card_holder_name: Mapped[str]
