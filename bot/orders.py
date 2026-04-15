from typing import Optional

from bot.client import BinanceClient, BinanceClientError
from bot.logging_config import setup_logger
from bot.validators import validate_order_inputs, ValidationError

logger = setup_logger("orders")


def place_order(
    client: BinanceClient,
    symbol: str,
    order_type: str,
    side: str,
    quantity: str,
    price: Optional[str] = None,
    stop_price: Optional[str] = None,
) -> dict:
    """
    Validate inputs then place an order via the Binance client.
    Returns the order response dict, or raises ValidationError / BinanceClientError.
    """
    validated = validate_order_inputs(
        symbol=symbol,
        order_type=order_type,
        side=side,
        quantity=quantity,
        price=price if order_type != "STOP_MARKET" else None,
    )

    # For STOP_MARKET, validate stop_price separately
    if validated["order_type"] == "STOP_MARKET":
        from bot.validators import validate_price
        if not stop_price:
            raise ValidationError("--stop-price is required for STOP_MARKET orders.")
        validated["stop_price"] = validate_price(stop_price)

    logger.debug("Validated order inputs: %s", validated)

    response = client.place_order(
        symbol=validated["symbol"],
        side=validated["side"],
        order_type=validated["order_type"],
        quantity=validated["quantity"],
        price=validated.get("price"),
        stop_price=validated.get("stop_price"),
    )

    return response
