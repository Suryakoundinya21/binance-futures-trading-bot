"""Order placement logic and result formatting."""
from __future__ import annotations

import logging
from typing import Optional

from .client import BinanceFuturesClient, BinanceAPIError
from .validators import (
    ValidationError,
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
)

logger = logging.getLogger("trading_bot.orders")


def format_order_summary(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str],
    stop_price: Optional[str],
) -> str:
    lines = [
        "─" * 50,
        "  ORDER REQUEST SUMMARY",
        "─" * 50,
        f"  Symbol     : {symbol}",
        f"  Side       : {side}",
        f"  Type       : {order_type}",
        f"  Quantity   : {quantity}",
    ]
    if price:
        lines.append(f"  Price      : {price}")
    if stop_price:
        lines.append(f"  Stop Price : {stop_price}")
    lines.append("─" * 50)
    return "\n".join(lines)


def format_order_response(response: dict) -> str:
    order_id   = response.get("orderId", "N/A")
    status     = response.get("status", "N/A")
    exec_qty   = response.get("executedQty", "N/A")
    avg_price  = response.get("avgPrice", "N/A")
    cum_quote  = response.get("cumQuote", "N/A")
    client_oid = response.get("clientOrderId", "N/A")

    lines = [
        "─" * 50,
        "  ORDER RESPONSE",
        "─" * 50,
        f"  Order ID       : {order_id}",
        f"  Client OID     : {client_oid}",
        f"  Status         : {status}",
        f"  Executed Qty   : {exec_qty}",
        f"  Avg Price      : {avg_price}",
        f"  Cumulative USD : {cum_quote}",
        "─" * 50,
    ]
    return "\n".join(lines)


def place_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
    stop_price: Optional[str] = None,
) -> dict:
    """Validate inputs, place order, log everything, return response dict."""

    # --- Validate ---
    try:
        symbol     = validate_symbol(symbol)
        side       = validate_side(side)
        order_type = validate_order_type(order_type)
        quantity   = validate_quantity(quantity)
        price      = validate_price(price, order_type)
        stop_price = validate_stop_price(stop_price, order_type)
    except ValidationError as exc:
        logger.error("Validation failed: %s", exc)
        raise

    # --- Summarise ---
    summary = format_order_summary(symbol, side, order_type, quantity, price, stop_price)
    logger.info("Placing order:\n%s", summary)
    print(summary)

    # --- Place ---
    try:
        response = client.place_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )
    except BinanceAPIError as exc:
        logger.error("API error placing order: %s", exc)
        raise
    except (ConnectionError, TimeoutError) as exc:
        logger.error("Network error placing order: %s", exc)
        raise

    # --- Display response ---
    response_str = format_order_response(response)
    logger.info("Order response:\n%s", response_str)
    print(response_str)
    print("  ✅  Order placed successfully!")

    return response
