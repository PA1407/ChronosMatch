
import streamlit as st
import pandas as pd

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from api_client import (
    check_api_health,
    submit_order,
    get_order,
    cancel_order,
    get_orderbook,
    get_orderbook_summary,
    get_trades,
    get_stats,
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------


st.set_page_config(
    page_title="ChronosMatch | Trading Dashboard",
    page_icon="📈",
    layout="wide",
)

IST = ZoneInfo("Asia/Kolkata")



# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def valid_symbol(value):
    """Validate trading symbols using backend rules."""
    return bool(
        value
        and len(value) <= 20
        and value.isalnum()
    )


def format_timestamp(value):
    """Convert UTC timestamps into Indian Standard Time."""
    if not value:
        return "N/A"

    try:
        if isinstance(value, datetime):
            timestamp = value
        else:
            timestamp = datetime.fromisoformat(
                str(value).replace("Z", "+00:00")
            )

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        return timestamp.astimezone(IST).strftime(
            "%d-%m-%Y %I:%M:%S %p IST"
        )

    except (ValueError, TypeError):
        return str(value)


def display_error(error):
    """Display API errors in a readable format."""
    response = getattr(error, "response", None)

    if response is not None:
        try:
            details = response.json()
            message = details.get("detail", str(details))
        except ValueError:
            message = response.text

        st.error(
            f"API Error ({response.status_code}): {message}"
        )
    else:
        st.error(f"Error: {error}")


def display_order_table(orders):
    """Display orders with timestamps converted to IST."""
    if not orders:
        st.info("No active orders.")
        return

    formatted_orders = []

    for order in orders:
        formatted_orders.append({
            "Order ID": order.get("order_id"),
            "Symbol": order.get("symbol"),
            "Side": order.get("side"),
            "Price": order.get("price", order.get("limit_price")),
            "Quantity": order.get("quantity"),
            "Filled Quantity": order.get("filled_quantity"),
            "Remaining Quantity": order.get("remaining_quantity"),
            "Status": order.get("status", order.get("order_status")),
            "Created At (IST)": format_timestamp(
                order.get("created_at")
            ),
            "Updated At (IST)": format_timestamp(
                order.get("updated_at")
            ),
        })

    st.dataframe(
        pd.DataFrame(formatted_orders),
        use_container_width=True,
        hide_index=True,
    )


def display_order_details(order):
    """Display order details in a clean table instead of raw JSON."""

    details = {
        "Order ID": order.get("order_id"),
        "Symbol": order.get("symbol"),
        "Side": order.get("side"),
        "Price": order.get("price", order.get("limit_price")),
        "Quantity": order.get("quantity"),
        "Filled Quantity": order.get("filled_quantity"),
        "Remaining Quantity": order.get("remaining_quantity"),
        "Status": order.get("status", order.get("order_status")),
    }

    st.dataframe(
        pd.DataFrame([details]),
        use_container_width=True,
        hide_index=True,
    )

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("Dashboard Controls")

symbol = st.sidebar.text_input(
    "Trading Symbol",
    value="ABC",
    max_chars=20,
).strip().upper()

if st.sidebar.button(
    "🔄 Refresh Dashboard",
    use_container_width=True,
):
    st.rerun()

st.sidebar.divider()
st.sidebar.caption("ChronosMatch Trading System")


# --------------------------------------------------
# HEADER
# --------------------------------------------------


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("📈 ChronosMatch")

st.caption(
    "Real-Time Order Management and Trading Dashboard"
)

st.caption(
    "All timestamps are displayed in Indian Standard Time (IST)."
)



# --------------------------------------------------
# BACKEND HEALTH CHECK
# --------------------------------------------------

api_online = check_api_health()

if api_online:
    st.success("🟢 Backend API is connected")
else:
    st.error("🔴 FastAPI: Offline")
    st.warning(
        "Start the FastAPI backend before using dashboard features."
    )


if not valid_symbol(symbol):
    st.warning(
        "Enter a valid symbol containing only letters and numbers."
    )
    st.stop()


# --------------------------------------------------
# MARKET OVERVIEW
# --------------------------------------------------

st.header("Market Overview")

if api_online:
    try:
        stats = get_stats()

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric(
            "Total Orders",
            stats.get("total_orders", 0),
        )

        col2.metric(
            "Active Orders",
            stats.get("active_orders", 0),
        )

        col3.metric(
            "Filled Orders",
            stats.get("filled_orders", 0),
        )

        col4.metric(
            "Cancelled Orders",
            stats.get("cancelled_orders", 0),
        )

        col5.metric(
            "Total Trades",
            stats.get("total_trades", 0),
        )

    except Exception as error:
        display_error(error)


st.divider()


# --------------------------------------------------
# DASHBOARD TABS
# --------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Order Book",
    "📝 Place Order",
    "🔍 Manage Orders",
    "📈 Trade History",
])



# ==================================================
# TAB 1: ORDER BOOK
# ==================================================

with tab1:

    st.header(f"Order Book — {symbol}")

    if api_online:
        try:
            summary = get_orderbook_summary(symbol)

            col1, col2, col3, col4 = st.columns(4)

            # These keys match app/api/orderbook.py.
            col1.metric(
                "Buy Orders",
                summary.get("buy_order_count", 0),
            )

            col2.metric(
                "Sell Orders",
                summary.get("sell_order_count", 0),
            )

            col3.metric(
                "Buy Remaining Quantity",
                summary.get("buy_remaining_quantity", 0),
            )

            col4.metric(
                "Sell Remaining Quantity",
                summary.get("sell_remaining_quantity", 0),
            )

            orderbook = get_orderbook(symbol)

            buy_orders = orderbook.get("buy_orders", [])
            sell_orders = orderbook.get("sell_orders", [])

            buy_col, sell_col = st.columns(2)

            with buy_col:
                st.subheader("🟢 Buy Orders")
                display_order_table(buy_orders)

            with sell_col:
                st.subheader("🔴 Sell Orders")
                display_order_table(sell_orders)

        except Exception as error:
            display_error(error)

    else:
        st.info(
            "Order book will be available when the backend is online."
        )


# ==================================================
# TAB 2: PLACE ORDER
# ==================================================

with tab2:

    st.header("Place New Order")

    with st.form("place_order_form"):

        order_symbol = st.text_input(
            "Trading Symbol",
            value=symbol,
            max_chars=20,
        ).strip().upper()

        side = st.selectbox(
            "Order Side",
            ["BUY", "SELL"],
        )

        limit_price = st.number_input(
            "Limit Price",
            min_value=0.01,
            value=100.0,
            step=1.0,
        )

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            value=10,
            step=1,
        )

        submitted = st.form_submit_button(
            "Submit Order",
            use_container_width=True,
        )

    if submitted:

        if not valid_symbol(order_symbol):
            st.error(
                "Enter a valid symbol containing only letters and numbers."
            )

        elif not api_online:
            st.error("Backend API is offline.")

        else:
            try:
                result = submit_order(
                    order_symbol,
                    side,
                    limit_price,
                    int(quantity),
                )

                st.session_state["last_order_result"] = result

                st.success(
                    "Order submitted successfully!"
                )

            except Exception as error:
                display_error(error)

    if st.session_state.get("last_order_result"):
       st.subheader("Submitted Order")
       display_order_details(
        st.session_state["last_order_result"]
    )


# ==================================================
# TAB 3: MANAGE ORDERS
# ==================================================

with tab3:

    st.header("Manage Existing Orders")

    order_id = st.text_input(
        "Enter Order ID",
        placeholder="Enter your order UUID",
    ).strip()

    find_col, cancel_col = st.columns(2)

    with find_col:
        find_clicked = st.button(
            "Find Order",
            use_container_width=True,
        )

    with cancel_col:
        cancel_clicked = st.button(
            "Cancel Order",
            use_container_width=True,
        )

    if find_clicked:

        if not order_id:
            st.warning("Please enter an Order ID.")

        elif not api_online:
            st.error("Backend API is offline.")

        else:
            try:
                order = get_order(order_id)

                st.session_state["found_order"] = order

                st.success("Order found.")

            except Exception as error:
                st.session_state.pop("found_order", None)
                display_error(error)

    if st.session_state.get("found_order"):

        order = st.session_state["found_order"]

        st.subheader("Order Details")

        order_details = {
            "Order ID": order.get("order_id"),
            "Symbol": order.get("symbol"),
            "Side": order.get("side"),
            "Limit Price": order.get("limit_price"),
            "Quantity": order.get("quantity"),
            "Remaining Quantity": order.get("remaining_quantity"),
            "Status": order.get("status"),
        }

        display_order_details(order)

    if cancel_clicked:

        if not order_id:
            st.warning("Please enter an Order ID.")

        elif not api_online:
            st.error("Backend API is offline.")

        else:
            try:
                result = cancel_order(order_id)

                st.session_state.pop("found_order", None)

                st.success("Order cancelled successfully!")

            except Exception as error:
                display_error(error)



# ==================================================
# TAB 4: TRADE HISTORY
# ==================================================

with tab4:

    st.header("Trade History")

    trade_limit = st.number_input(
        "Number of Recent Trades",
        min_value=1,
        max_value=1000,
        value=100,
        step=10,
    )

    if st.button(
        "Load Trade History",
        use_container_width=True,
    ):

        if not api_online:
            st.error("Backend API is offline.")

        else:
            try:
                trades = get_trades(
                    symbol=symbol,
                    limit=int(trade_limit),
                )

                st.session_state["trade_history"] = trades

            except Exception as error:
                display_error(error)

    if "trade_history" in st.session_state:

        trades = st.session_state["trade_history"]

        if trades:

            formatted_trades = []

            for trade in trades:
                formatted_trades.append({
                    "Trade ID": trade.get("trade_id"),
                    "Symbol": trade.get("symbol"),
                    "Buy Order ID": trade.get("buy_order_id"),
                    "Sell Order ID": trade.get("sell_order_id"),
                    "Execution Price": trade.get(
                        "execution_price",
                        trade.get("price"),
                    ),
                    "Quantity": trade.get("quantity"),
                    "Executed At (IST)": format_timestamp(
                        trade.get("executed_at")
                    ),
                })

            st.dataframe(
                pd.DataFrame(formatted_trades),
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.info("No trades found for this symbol.")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------


st.divider()

st.caption("ChronosMatch")