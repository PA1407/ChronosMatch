
import streamlit as st
import pandas as pd
import requests

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
    page_title="ChronosMatch Trading Dashboard",
    page_icon="📈",
    layout="wide",
)

st.title("📈 ChronosMatch")
st.caption("Zero-Copy High-Frequency Trading Engine | Trading Dashboard")

# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def show_api_error(error):
    """Display a useful API error message."""
    if isinstance(error, requests.HTTPError):
        response = error.response
        if response is not None:
            try:
                detail = response.json().get("detail", response.text)
            except ValueError:
                detail = response.text

            st.error(f"API Error ({response.status_code}): {detail}")
            return

    st.error(f"Connection error: {error}")


def dataframe_or_empty(records, message):
    """Display records as a table or show an empty-state message."""
    if records:
        st.dataframe(
            pd.DataFrame(records),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info(message)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("Dashboard Controls")

symbol = st.sidebar.text_input(
    "Trading Symbol",
    value="ABC",
    max_chars=20,
).strip().upper()

refresh = st.sidebar.button(
    "🔄 Refresh Dashboard",
    use_container_width=True,
)

st.sidebar.divider()

# --------------------------------------------------
# API CONNECTION STATUS
# --------------------------------------------------

api_online = check_api_health()

if api_online:
    st.success("Backend API is connected")
else:
    st.error(
        "Backend API is offline. Start the FastAPI server "
        "before using dashboard features."
    )

if not symbol or not symbol.isalnum():
    st.warning("Enter a valid symbol containing letters and numbers.")
    st.stop()

# --------------------------------------------------
# STATISTICS
# --------------------------------------------------

st.header("Market Overview")

if api_online:
    try:
        stats = get_stats()

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Total Orders", stats.get("total_orders", 0))
        col2.metric("Active Orders", stats.get("active_orders", 0))
        col3.metric("Filled Orders", stats.get("filled_orders", 0))
        col4.metric("Cancelled Orders", stats.get("cancelled_orders", 0))
        col5.metric("Total Trades", stats.get("total_trades", 0))

    except requests.RequestException as error:
        show_api_error(error)

st.divider()

# --------------------------------------------------
# MAIN DASHBOARD TABS
# --------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Order Book",
    "📝 Place Order",
    "🔍 Manage Orders",
    "💹 Trade History",
])

# --------------------------------------------------
# TAB 1: ORDER BOOK
# --------------------------------------------------

with tab1:
    st.subheader(f"Order Book — {symbol}")

    if api_online:
        try:
            book = get_orderbook(symbol)
            summary = get_orderbook_summary(symbol)

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("Buy Orders", summary.get("buy_order_count", 0))
            c2.metric("Sell Orders", summary.get("sell_order_count", 0))
            c3.metric(
                "Buy Remaining Quantity",
                summary.get("buy_remaining_quantity", 0),
            )
            c4.metric(
                "Sell Remaining Quantity",
                summary.get("sell_remaining_quantity", 0),
            )

            buy_col, sell_col = st.columns(2)

            with buy_col:
                st.markdown("### 🟢 Buy Orders")
                dataframe_or_empty(
                    book.get("buy_orders", []),
                    "No active buy orders.",
                )

            with sell_col:
                st.markdown("### 🔴 Sell Orders")
                dataframe_or_empty(
                    book.get("sell_orders", []),
                    "No active sell orders.",
                )

        except requests.RequestException as error:
            show_api_error(error)

# --------------------------------------------------
# TAB 2: PLACE ORDER
# --------------------------------------------------

with tab2:
    st.subheader("Submit a New Order")

    with st.form("order_form"):
        order_symbol = st.text_input(
            "Symbol",
            value=symbol,
        ).strip().upper()

        side = st.selectbox(
            "Order Side",
            ["BUY", "SELL"],
        )

        price = st.number_input(
            "Limit Price",
            min_value=0.01,
            value=100.00,
            step=1.0,
            format="%.2f",
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
        if not order_symbol or not order_symbol.isalnum():
            st.warning("Enter a valid trading symbol.")
        elif not api_online:
            st.error("Backend is offline. Cannot submit order.")
        else:
            try:
                result = submit_order(
                    order_symbol,
                    side,
                    price,
                    int(quantity),
                )

                st.success("Order submitted successfully!")
                st.json(result)

            except requests.RequestException as error:
                show_api_error(error)

# --------------------------------------------------
# TAB 3: ORDER LOOKUP AND CANCELLATION
# --------------------------------------------------

with tab3:
    st.subheader("Manage Existing Orders")

    order_id = st.text_input("Enter Order ID")

    lookup_col, cancel_col = st.columns(2)

    with lookup_col:
        if st.button("Find Order", use_container_width=True):
            if not order_id.strip():
                st.warning("Please enter an order ID.")
            elif not api_online:
                st.error("Backend is offline.")
            else:
                try:
                    result = get_order(order_id.strip())
                    st.success("Order found.")
                    st.json(result)

                except requests.RequestException as error:
                    show_api_error(error)

    with cancel_col:
        if st.button("Cancel Order", use_container_width=True):
            if not order_id.strip():
                st.warning("Please enter an order ID.")
            elif not api_online:
                st.error("Backend is offline.")
            else:
                try:
                    result = cancel_order(order_id.strip())
                    st.success("Order cancellation response received.")
                    st.json(result)

                except requests.RequestException as error:
                    show_api_error(error)

# --------------------------------------------------
# TAB 4: TRADE HISTORY
# --------------------------------------------------

with tab4:
    st.subheader("Recent Executed Trades")

    trade_limit = st.slider(
        "Number of trades",
        min_value=1,
        max_value=100,
        value=20,
    )

    if api_online:
        try:
            trades = get_trades(
                symbol=symbol,
                limit=trade_limit,
            )

            dataframe_or_empty(
                trades,
                "No trades found for this symbol.",
            )

        except requests.RequestException as error:
            show_api_error(error)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "ChronosMatch | Python • FastAPI • SQLite • Streamlit"
)
