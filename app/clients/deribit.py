import asyncio
import time
from decimal import Decimal
import aiohttp

from pydantic import AnyHttpUrl


class DeribitClient:
    def __init__(self, base_url: str | AnyHttpUrl, timeout: float = 10.0):
        self._base_url = str(base_url).rstrip("/")
        self._timeout = aiohttp.ClientTimeout(total=timeout)

    SUPPORTED_TICKERS = frozenset({"btc_usd", "eth_usd"})

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

        url = f"{self._base_url}/get_index_price"
        params = {"index_name": ticker}

        try:
            async with aiohttp.ClientSession(timeout=self._timeout) as session:
                async with session.get(url, params=params) as response:
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
