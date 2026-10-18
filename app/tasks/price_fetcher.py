import asyncio

from app.celery_app import celery_app
from app.clients.deribit import DeribitClient
from app.db.repository import PriceRepository
from app.db.session import SessionLocal
from app.schemas.prices import PriceCreate


async def _fetch_prices():
    client = DeribitClient()
    btc_data, eth_data = await asyncio.gather(
        client.get_index_price("BTC"), client.get_index_price("ETH")
    )

    return [("btc_usd", btc_data), ("eth_usd", eth_data)]


@celery_app.task
def fetch_and_save_prices():
    try:
        results = asyncio.run(_fetch_prices())
    except Exception as e:
        print(f"Не удалось получить данные с биржи: {e}")
        return

    db = SessionLocal()
    repo = PriceRepository(db)

    try:
        for ticker, data in results:
            price = data["price"]
            timestamp = data["timestamp"]

            price_create = PriceCreate(ticker=ticker, price=price, timestamp=timestamp)
            repo.create(price_create)

        print(f"Успешно сохранено {len(results)} записей в БД")

    except Exception as e:
        print(f"Ошибка при сохранении в БД: {e}")
        db.rollback()

    finally:
        db.close()
