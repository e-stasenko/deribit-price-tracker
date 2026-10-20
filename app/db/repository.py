from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Price
from app.schemas.prices import PriceCreate


class PriceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, price_data: PriceCreate) -> Price:
        db_price = Price(**price_data.model_dump())
        self.db.add(db_price)
        self.db.flush()
        self.db.refresh(db_price)
        return db_price

    def get_latest(self, ticker: str) -> Price | None:
        """Получение последней цены валюты."""
        stmt = (
            select(Price)
            .where(Price.ticker == ticker)
            .order_by(Price.timestamp.desc())
            .limit(1)
        )
        return self.db.scalars(stmt).first()

    def get_all_by_ticker(self, ticker: str) -> Sequence[Price]:
        """Получение всех сохраненных данных по указанной валюте."""
        stmt = (
            select(Price).where(Price.ticker == ticker).order_by(Price.timestamp.desc())
        )
        return self.db.scalars(stmt).all()

    def get_history(
        self,
        ticker: str,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> Sequence[Price]:
        """Получение цены валюты с фильтром по дате (UNIX timestamp)."""
        stmt = select(Price).where(Price.ticker == ticker)
        if start_time is not None:
            stmt = stmt.where(Price.timestamp >= start_time)

        if end_time is not None:
            stmt = stmt.where(Price.timestamp <= end_time)

        stmt = stmt.order_by(Price.timestamp.desc())
        return self.db.scalars(stmt).all()
