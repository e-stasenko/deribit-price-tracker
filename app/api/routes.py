from datetime import datetime, timezone
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_price_repository
from app.db.repository import PriceRepository
from app.schemas.prices import PriceRead

router = APIRouter(prefix="/prices", tags=["Prices"])

TickerQuery = Annotated[
    Literal["btc_usd", "eth_usd"],
    Query(..., description="Обязательный тикер криптовалюты: 'btc_usd' или 'eth_usd'"),
]


def _to_unix_timestamp(value: int | datetime | None) -> int | None:
    """Конвертирует входной параметр даты (int или datetime) в секунды UNIX."""
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return int(value.timestamp())


@router.get(
    "/",
    response_model=list[PriceRead],
    summary="Получение всех сохраненных данных по указанной криптовалюте",
)
def get_all_prices(
    ticker: TickerQuery,
    repo: PriceRepository = Depends(get_price_repository),
) -> list[PriceRead]:
    return list(repo.get_all_by_ticker(ticker=ticker))


@router.get(
    "/latest",
    response_model=PriceRead,
    summary="Получение последней цены криптовалюты",
)
def get_latest_price(
    ticker: TickerQuery,
    repo: PriceRepository = Depends(get_price_repository),
) -> PriceRead:
    price = repo.get_latest(ticker=ticker)
    if price is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Данные по тикеру '{ticker}' еще не найдены.",
        )
    return price


@router.get(
    "/filter",
    response_model=list[PriceRead],
    summary="Получение цены криптовалюты с фильтром по дате",
)
def get_prices_by_date(
    ticker: TickerQuery,
    start_date: Annotated[
        int | datetime | None,
        Query(description="Начало периода"),
    ] = None,
    end_date: Annotated[
        int | datetime | None,
        Query(description="Конец периода"),
    ] = None,
    repo: PriceRepository = Depends(get_price_repository),
) -> list[PriceRead]:
    start_ts = _to_unix_timestamp(start_date)
    end_ts = _to_unix_timestamp(end_date)

    if start_ts is not None and end_ts is not None and start_ts > end_ts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Начальная дата (start_date) не может быть больше конечной (end_date).",
        )

    return list(
        repo.get_history(
            ticker=ticker,
            start_time=start_ts,
            end_time=end_ts,
        )
    )
