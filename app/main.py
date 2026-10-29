
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.success import router as success_router
from app.api.orders import router as orders_router
from app.api.trades import router as trades_router
from app.api.stats import router as stats_router
from app.api.orderbook import router as orderbook_router
from app.services.order_service import matching_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Restore the shared matching engine before serving requests."""
    matching_engine.restore_from_database()
    yield


app = FastAPI(
    title="ChronusMatch",
    lifespan=lifespan,
)

app.include_router(success_router)
app.include_router(orders_router)
app.include_router(trades_router)
app.include_router(stats_router)
app.include_router(orderbook_router)
