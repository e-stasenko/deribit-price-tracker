import asyncio
import time
from decimal import Decimal

import aiohttp


class DeribitClient:
    BASE_URL = "https://www.deribit.com/api/v2/public"
    TICKER_MAP = {"BTC": "btc_usd", "ETH": "eth_usd"}

    async def get_index_price(self, ticker: str) -> dict:
        """
        Получает текущую цену и время получения с биржи Deribit.
        Возвращает словарь: {"price": Decimal, "timestamp": int}
        """
        if ticker not in self.TICKER_MAP:
            raise ValueError(
                f"Тикер {ticker} не поддерживается. Доступны: {list(self.TICKER_MAP.keys())}"
            )

        deribit_ticker = self.TICKER_MAP[ticker]
        url = f"{self.BASE_URL}/get_index_price"
        params = {"index_name": deribit_ticker}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    response.raise_for_status()

                    data = await response.json()

                    timestamp = int(time.time())
                    price = Decimal(str(data["result"]["index_price"]))

                    return {"price": price, "timestamp": timestamp}

        except aiohttp.ClientError as e:
            print(f"[DeribitClient] Ошибка сети при запросе {ticker}: {e}")
            raise ConnectionError(f"Не удалось получить цену с Deribit: {e}")

        except asyncio.TimeoutError:
            print(f"[DeribitClient] Таймаут при запросе {ticker}")
            raise TimeoutError("Deribit не ответил вовремя")
