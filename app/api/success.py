from fastapi import APIRouter, HTTPException
from app.database.connection import get_connection

router = APIRouter(tags=["Success"])

@router.get("/success")
def success():
    try:
        with get_connection() as connection:
            connection.execute("SELECT 1")

        return {
            "status": "success",
            "database": "connected"
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "failure",
                "database": "disconnected"
            }
        )