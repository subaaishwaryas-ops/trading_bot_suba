#!/usr/bin/env python3
"""
Binance Futures Testnet Trading Bot — CLI entry point.

Usage examples:
  python cli.py place --symbol BTCUSDT --type MARKET --side BUY --quantity 0.001
  python cli.py place --symbol BTCUSDT --type LIMIT  --side SELL --quantity 0.001 --price 95000
  python cli.py place --symbol BTCUSDT --type STOP_MARKET --side SELL --quantity 0.001 --stop-price 85000
  python cli.py account
"""

import argparse
import json
import os
import sys

from bot.client import BinanceClient, BinanceClientError
from bot.logging_config import setup_logger
from bot.orders import place_order
from bot.validators import ValidationError

logger = setup_logger("cli")

# ------------------------------------------------------------------ #
#  Helpers                                                             #
# ------------------------------------------------------------------ #

BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def _header(text: str):
    print(f"\n{BOLD}{CYAN}{'─'*50}{RESET}")
    print(f"{BOLD}{CYAN}  {text}{RESET}")
    print(f"{BOLD}{CYAN}{'─'*50}{RESET}")


def _success(text: str):
    print(f"{GREEN}✔  {text}{RESET}")


def _error(text: str):
    print(f"{RED}✘  {text}{RESET}")


def _info(label: str, value):
    print(f"  {YELLOW}{label:<20}{RESET}{value}")


def _get_client() -> BinanceClient:
    api_key = os.environ.get("BINANCE_API_KEY", "").strip()
    api_secret = os.environ.get("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        _error(
            "API credentials not set.\n"
            "  Export them before running:\n"
            "    set BINANCE_API_KEY=your_key      (Windows)\n"
            "    set BINANCE_API_SECRET=your_secret\n"
            "  or:\n"
            "    export BINANCE_API_KEY=your_key   (Linux/Mac)\n"
            "    export BINANCE_API_SECRET=your_secret"
        )
        sys.exit(1)

    return BinanceClient(api_key, api_secret)


# ------------------------------------------------------------------ #
#  Sub-command handlers                                               #
# ------------------------------------------------------------------ #

def cmd_place(args):
    _header("ORDER REQUEST")
    _info("Symbol:", args.symbol.upper())
    _info("Type:", args.type.upper())
    _info("Side:", args.side.upper())
    _info("Quantity:", args.quantity)
    if args.price:
        _info("Price:", args.price)
    if args.stop_price:
        _info("Stop Price:", args.stop_price)

    logger.info(
        "CLI order request | symbol=%s type=%s side=%s qty=%s price=%s stop=%s",
        args.symbol, args.type, args.side, args.quantity, args.price, args.stop_price,
    )

    client = _get_client()

    try:
        response = place_order(
            client=client,
            symbol=args.symbol,
            order_type=args.type,
            side=args.side,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValidationError as exc:
        _error(f"Validation failed: {exc}")
        logger.warning("Validation error: %s", exc)
        sys.exit(1)
    except BinanceClientError as exc:
        _error(f"API error (code={exc.code}): {exc}")
        logger.error("BinanceClientError: code=%s | %s", exc.code, exc)
        sys.exit(1)

    _header("ORDER RESPONSE")
    _info("Order ID:", response.get("orderId", "N/A"))
    _info("Client Order ID:", response.get("clientOrderId", "N/A"))
    _info("Symbol:", response.get("symbol", "N/A"))
    _info("Status:", response.get("status", "N/A"))
    _info("Side:", response.get("side", "N/A"))
    _info("Type:", response.get("type", "N/A"))
    _info("Orig Qty:", response.get("origQty", "N/A"))
    _info("Executed Qty:", response.get("executedQty", "N/A"))
    _info("Avg Price:", response.get("avgPrice", "N/A"))
    _info("Price:", response.get("price", "N/A"))

    print()
    _success("Order placed successfully!")
    logger.info("Order response: %s", json.dumps(response))


def cmd_account(args):
    _header("ACCOUNT INFO")
    client = _get_client()
    try:
        info = client.get_account_info()
    except BinanceClientError as exc:
        _error(f"API error: {exc}")
        sys.exit(1)

    _info("Total Wallet Bal:", info.get("totalWalletBalance", "N/A"))
    _info("Avail Balance:", info.get("availableBalance", "N/A"))
    _info("Total UnPnl:", info.get("totalUnrealizedProfit", "N/A"))
    _info("Can Trade:", info.get("canTrade", "N/A"))
    print()


# ------------------------------------------------------------------ #
#  Argument parser                                                     #
# ------------------------------------------------------------------ #

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py place --symbol BTCUSDT --type MARKET --side BUY --quantity 0.001
  python cli.py place --symbol BTCUSDT --type LIMIT  --side SELL --quantity 0.001 --price 95000
  python cli.py place --symbol BTCUSDT --type STOP_MARKET --side SELL --quantity 0.001 --stop-price 85000
  python cli.py account
        """,
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # --- place ---
    p = sub.add_parser("place", help="Place a new order")
    p.add_argument("--symbol",     required=True, help="Trading pair, e.g. BTCUSDT")
    p.add_argument("--type",       required=True, help="MARKET | LIMIT | STOP_MARKET")
    p.add_argument("--side",       required=True, help="BUY | SELL")
    p.add_argument("--quantity",   required=True, help="Order quantity")
    p.add_argument("--price",      default=None,  help="Limit price (required for LIMIT)")
    p.add_argument("--stop-price", dest="stop_price", default=None,
                   help="Stop price (required for STOP_MARKET)")

    # --- account ---
    sub.add_parser("account", help="Show futures account summary")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "place":   cmd_place,
        "account": cmd_account,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
