from decimal import Decimal, InvalidOperation


VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}
VALID_SIDES = {"BUY", "SELL"}


class ValidationError(Exception):
    pass


def validate_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not s or not s.isalnum():
        raise ValidationError(f"Invalid symbol '{symbol}'. Must be alphanumeric, e.g. BTCUSDT.")
    return s


def validate_order_type(order_type: str) -> str:
    ot = order_type.strip().upper()
    if ot not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    return ot


def validate_side(side: str) -> str:
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValidationError(f"Invalid side '{side}'. Must be BUY or SELL.")
    return s


def validate_quantity(quantity: str) -> str:
    try:
        val = Decimal(quantity)
        if val <= 0:
            raise ValidationError("Quantity must be greater than zero.")
    except InvalidOperation:
        raise ValidationError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    return str(val)


def validate_price(price: str) -> str:
    try:
        val = Decimal(price)
        if val <= 0:
            raise ValidationError("Price must be greater than zero.")
    except InvalidOperation:
        raise ValidationError(f"Invalid price '{price}'. Must be a positive number.")
    return str(val)


def validate_order_inputs(symbol, order_type, side, quantity, price=None):
    """Validate all order inputs together. Returns a dict of validated values."""
    validated = {
        "symbol": validate_symbol(symbol),
        "order_type": validate_order_type(order_type),
        "side": validate_side(side),
        "quantity": validate_quantity(quantity),
    }

    if validated["order_type"] in ("LIMIT", "STOP_MARKET"):
        if price is None:
            raise ValidationError(f"Price is required for {validated['order_type']} orders.")
        validated["price"] = validate_price(price)
    elif price is not None:
        validated["price"] = validate_price(price)  # Accept but won't use for MARKET

    return validated
