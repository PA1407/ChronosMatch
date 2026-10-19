from fastapi import FastAPI
from app.api.success import router as success_router
from app.api.orders import router as orders_router
from app.api.trades import router as trades_router
from app.api.stats import router as stats_router

app = FastAPI(title="ChronusMatch")
app.include_router(success_router)
app.include_router(orders_router)
app.include_router(trades_router)
app.include_router(stats_router)