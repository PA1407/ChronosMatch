
from fastapi import APIRouter, HTTPException, status

from app.schemas.order import OrderCreate, OrderResponse
from app.database.repository import get_order as find_order
from app.database.repository import update_order
from app.services.order_service import submit_order, matching_engine

router = APIRouter(prefix="/orders", tags=["Orders"])


def to_response(record: dict) -> OrderResponse:
    return OrderResponse(
        order_id=record["order_id"],
        symbol=record["symbol"],
        side=record["side"],
        limit_price=record["limit_price"],
        quantity=record["quantity"],
        remaining_quantity=record["remaining_quantity"],
        status=record["status"],
    )


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(order: OrderCreate):
    try:
        saved = submit_order(order)
        return to_response(saved)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: str):
    record = find_order(order_id)

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return to_response(record)


@router.delete("/{order_id}", response_model=OrderResponse)
def cancel_order(order_id: str):
    record = find_order(order_id)

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    if record["status"] in ("FILLED", "CANCELLED"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Order cannot be cancelled",
        )

    # Remove the order from the matching engine if it is resting.
    engine_order = matching_engine.get_order(
        record["symbol"],
        order_id,
    )

    if engine_order is not None:
        cancelled = matching_engine.cancel_order(
            record["symbol"],
            order_id,
        )

        if not cancelled:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Unable to cancel order in matching engine",
            )

    updated = update_order(
        order_id,
        {
            "status": "CANCELLED",
            "remaining_quantity": 0,
        },
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return to_response(updated)
