import asyncio
import logging

from app.celery_app import celery_app
from app.clients.deribit import DeribitClient
from app.core.config import get_settings
from app.db.repository import PriceRepository
from app.db.session import SessionLocal
from app.schemas.prices import PriceCreate

logger = logging.getLogger(__name__)


async def _fetch_prices() -> list[dict]:
    async with DeribitClient(base_url=get_settings().DERIBIT_BASE_URL) as client:
        tickers = sorted(DeribitClient.SUPPORTED_TICKERS)
        results = await asyncio.gather(*(client.get_index_price(t) for t in tickers))
        return list(results)


@celery_app.task
def fetch_and_save_prices():
    try:
        results = asyncio.run(_fetch_prices())
    except Exception as e:
        logger.error("fetch from Deribit failed: %s", e)
        return {"saved": 0, "failed": 0, "error": str(e)}

    db = SessionLocal()
    repo = PriceRepository(db)

    saved = 0
    failed = 0
    try:
        for item in results:
            try:
                price_create = PriceCreate(
                    ticker=item["ticker"],
                    price=item["price"],
                    timestamp=item["timestamp"],
                )
                repo.create(price_create)
                saved += 1
            except Exception as e:
                failed += 1
                logger.warning("save failed for ticker=%s: %s", item.get("ticker"), e)

        if saved:
            db.commit()

        logger.info("prices saved: %d, failed: %d", saved, failed)
        return {"saved": saved, "failed": failed}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
