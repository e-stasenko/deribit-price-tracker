import asyncio
import time
from decimal import Decimal

import aiohttp
from pydantic import AnyHttpUrl


class DeribitClient:
    SUPPORTED_TICKERS = frozenset({"btc_usd", "eth_usd"})

    def __init__(self, base_url: str | AnyHttpUrl, timeout: float = 10.0) -> None:
        self._base_url = str(base_url).rstrip("/")
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "DeribitClient":
        self._session = aiohttp.ClientSession(timeout=self._timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_index_price(self, ticker: str) -> dict:
        """
        ticker — формат Deribit и формат хранения: 'btc_usd' | 'eth_usd'.
        Возвращает: {"ticker": str, "price": Decimal, "timestamp": int}
        """
        if ticker not in self.SUPPORTED_TICKERS:
            raise ValueError(
                f"Unsupported ticker {ticker!r}; "
                f"available: {sorted(self.SUPPORTED_TICKERS)}"
            )

        if self._session is None or self._session.closed:
            raise RuntimeError(
                "Use DeribitClient inside 'async with DeribitClient(...) as client:'"
            )

        url = f"{self._base_url}/get_index_price"
        params = {"index_name": ticker}

        try:
            async with self._session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
        except asyncio.TimeoutError as e:
            raise TimeoutError(f"Deribit timeout for {ticker}") from e
        except aiohttp.ClientError as e:
            raise ConnectionError(f"Deribit request failed for {ticker}: {e}") from e

        result = data.get("result")
        if not isinstance(result, dict) or "index_price" not in result:
            raise ValueError(f"Unexpected Deribit payload for {ticker}: {data}")

        return {
            "ticker": ticker,
            "price": Decimal(str(result["index_price"])),
            "timestamp": int(time.time()),
        }
