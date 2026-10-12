from fastapi import FastAPI
from app.api.success import router as success_router
from app.api.orders import router as orders_router

app = FastAPI(title="ChronusMatch")
app.include_router(success_router)
app.include_router(orders_router)