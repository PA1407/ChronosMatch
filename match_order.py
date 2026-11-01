def match_orders(buy_order, sell_order):
    # Check whether prices are compatible
    if buy_order["price"] < sell_order["price"]:
        return "No trade: prices do not match"

    # Find the quantity that both orders can fulfill
    traded_quantity = min(
        buy_order["quantity"],
        sell_order["quantity"]
    )

    # Update remaining quantities
    buy_order["quantity"] -= traded_quantity
    sell_order["quantity"] -= traded_quantity

    # Return trade details
    return {
        "trade_price": sell_order["price"],
        "trade_quantity": traded_quantity,
        "buyer_remaining": buy_order["quantity"],
        "seller_remaining": sell_order["quantity"]
    }
buyer = {"price": 100, "quantity": 10}
seller = {"price": 100, "quantity": 6}

result = match_orders(buyer, seller)
print(result)