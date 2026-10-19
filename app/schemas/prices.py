from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PriceBase(BaseModel):
    ticker: Literal["btc_usd", "eth_usd"] = Field(
        ..., max_length=25, description="Тикер (BTC или ETH)"
    )
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
