
from fastapi import APIRouter

from app.database.repository import get_order_stats

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("")
def get_stats():
    return get_order_stats()
