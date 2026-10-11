from fastapi import APIRouter
router = APIRouter()
@router.get("/success")
def success():
    return {"status": "Success!"}