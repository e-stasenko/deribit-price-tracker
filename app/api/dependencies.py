from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.repository import PriceRepository
from app.db.session import get_db


def get_price_repository(db: Session = Depends(get_db)) -> PriceRepository:
    """Провайдер зависимости для внедрения репозитория цен в эндпоинты."""
    return PriceRepository(db=db)
