from fastapi import FastAPI
from app.api.success import router as success_router

app = FastAPI(title="ChronusMatch")
app.include_router(success_router)