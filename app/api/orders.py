
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.schemas.order import OrderCreate, OrderResponse, OrderStatus

router = APIRouter(prefix="/orders", tags=["Orders"])
_orders: dict[str, OrderResponse] = {}


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(order: OrderCreate):
    order_id = str(uuid4())

    new_order = OrderResponse(
        order_id=order_id,
        symbol=order.symbol,
        side=order.side,
        limit_price=order.limit_price,
        quantity=order.quantity,
        remaining_quantity=order.quantity,
        status=OrderStatus.NEW,
    )

    _orders[order_id] = new_order
    return new_order


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: str):
    order = _orders.get(order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return order


@router.delete("/{order_id}", response_model=OrderResponse)
def cancel_order(order_id: str):
    order = _orders.get(order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    if order.status in (OrderStatus.FILLED, OrderStatus.CANCELLED):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot cancel an order with status {order.status.value}",
        )

    cancelled_order = order.model_copy(
        update={"status": OrderStatus.CANCELLED, "remaining_quantity": 0}
    )

    _orders[order_id] = cancelled_order
    return cancelled_order
