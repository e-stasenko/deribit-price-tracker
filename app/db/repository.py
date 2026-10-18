from sqlalchemy.orm import Session
from typing import Optional

from app.db.models import Price
from app.schemas.price import PriceCreate


class PriceRepository:
    def __init__(self, db:Session):
        self.db = db

    
    def create(self, price_data: PriceCreate) -> Price:
        db_price = Price(**price_data.model_dump())
        self.db.add(db_price)
        self.db.commit()
        self.db.refresh(db_price)
        return db_price

    def get_latest(self, ticker: str) -> Price | None:
        query = (
            self.db.query(Price)
            .filter(Price.ticker == ticker)
            .order_by(Price.timestamp.desc())
        )
        return query.first()

    def get_history(
        self, 
        ticker: str, 
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 100,
    ) -> list[Price]:
        query = self.db.query(Price).filter(Price.ticker == ticker)

        if start_time is not None:
            query = query.filter(Price.timestamp >= start_time)

        if end_time is not None:
            query = query.filter(Price.timestamp <= end_time)

        return (
            query
            .order_by(Price.timestamp.desc())
            .limit(limit)
            .all()
        )
