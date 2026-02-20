"""Input validation helpers."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Optional

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


class ValidationError(ValueError):
    """Raised when user-supplied input fails validation."""


def validate_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not s or not s.isalnum():
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Must be alphanumeric (e.g. BTCUSDT)."
        )
    return s


def validate_side(side: str) -> str:
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValidationError(
            f"Invalid side '{side}'. Must be one of: {', '.join(VALID_SIDES)}."
        )
    return s


def validate_order_type(order_type: str) -> str:
    t = order_type.strip().upper()
    if t not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(VALID_ORDER_TYPES)}."
        )
    return t


def validate_quantity(quantity: str) -> str:
    try:
        qty = Decimal(quantity)
    except InvalidOperation:
        raise ValidationError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if qty <= 0:
        raise ValidationError(f"Quantity must be greater than 0, got '{quantity}'.")
    return str(qty)


def validate_price(price: Optional[str], order_type: str) -> Optional[str]:
    if order_type == "MARKET":
        return None  # price not required for market orders

    if order_type in {"LIMIT", "STOP_MARKET"} and not price:
        raise ValidationError(f"Price is required for {order_type} orders.")

    try:
        p = Decimal(price)
    except InvalidOperation:
        raise ValidationError(f"Invalid price '{price}'. Must be a positive number.")
    if p <= 0:
        raise ValidationError(f"Price must be greater than 0, got '{price}'.")
    return str(p)


def validate_stop_price(stop_price: Optional[str], order_type: str) -> Optional[str]:
    if order_type != "STOP_MARKET":
        return None
    if not stop_price:
        raise ValidationError("Stop price is required for STOP_MARKET orders.")
    try:
        sp = Decimal(stop_price)
    except InvalidOperation:
        raise ValidationError(f"Invalid stop price '{stop_price}'.")
    if sp <= 0:
        raise ValidationError("Stop price must be greater than 0.")
    return str(sp)
