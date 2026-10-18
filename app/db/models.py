from decimal import Decimal

from sqlalchemy import BigInteger, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Price(Base):
    """Модель цены."""

    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(25), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    timestamp: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)

    def __repr__(self) -> str:
        return (
            f"Price(id={self.id}, ticker={self.ticker!r}, "
            f"price={self.price}, timestamp={self.timestamp})"
        )

    __table_args__ = (Index("ix_prices_ticker_timestamp", "ticker", "timestamp"),)
