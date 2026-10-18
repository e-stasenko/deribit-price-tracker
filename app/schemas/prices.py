from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict, field_validator


class PriceBase(BaseModel):
    ticker: str = Field(..., max_length=25, description="Тикер")
    price: Decimal = Field(..., gt=0, description="Цена")
    timestamp: int = Field(..., gt=0, description="UNIX время")


class PriceCreate(PriceBase):

    model_config = ConfigDict(extra="forbid")

    @field_validator("ticker")
    @classmethod
    def ticker_cannot_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Тикер не может пустым!")
        return value


class PriceRead(PriceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
