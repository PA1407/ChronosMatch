
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from app.schemas.order import OrderCreate, OrderResponse, OrderStatus
from app.database.repository import (
    create_order as save_order,
    get_order as find_order,
    update_order,
)

router = APIRouter(prefix="/orders", tags=["Orders"])


def current_time():
    return datetime.now(timezone.utc).isoformat()


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
    now = current_time()

    order_data = {
        "order_id": str(uuid4()),
        "symbol": order.symbol,
        "side": order.side,
        "limit_price": order.limit_price,
        "quantity": order.quantity,
        "remaining_quantity": order.quantity,
        "status": OrderStatus.NEW,
        "created_at": now,
        "updated_at": now,
    }

    saved = save_order(order_data)
    return to_response(saved)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: str):
    record = find_order(order_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    return to_response(record)


@router.delete("/{order_id}", response_model=OrderResponse)
def cancel_order(order_id: str):
    record = find_order(order_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    if record["status"] in ("FILLED", "CANCELLED"):
        raise HTTPException(
            status_code=409,
            detail="Order cannot be cancelled",
        )

    updated = update_order(
        order_id,
        {
            "status": OrderStatus.CANCELLED,
            "remaining_quantity": 0,
        },
    )

    return to_response(updated)
