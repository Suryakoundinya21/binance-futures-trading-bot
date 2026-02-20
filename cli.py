#!/usr/bin/env python3
"""
CLI entry point for the Binance Futures Testnet trading bot.

Usage examples:
  # Market BUY
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

  # Limit SELL
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 100000

  # Stop-Market BUY (bonus)
  python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 95000
"""
from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

from bot.logging_config import setup_logging
from bot.client import BinanceFuturesClient, BinanceAPIError
from bot.orders import place_order
from bot.validators import ValidationError

# --------------------------------------------------------------------------- #
#  Bootstrap                                                                   #
# --------------------------------------------------------------------------- #

load_dotenv()
logger = setup_logging()


# --------------------------------------------------------------------------- #
#  Argument parsing                                                            #
# --------------------------------------------------------------------------- #

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet – order placement CLI",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--symbol", required=True,
        help="Trading pair symbol, e.g. BTCUSDT",
    )
    parser.add_argument(
        "--side", required=True, choices=["BUY", "SELL"],
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "--type", dest="order_type", required=True,
        choices=["MARKET", "LIMIT", "STOP_MARKET"],
        help="Order type: MARKET, LIMIT, or STOP_MARKET",
    )
    parser.add_argument(
        "--quantity", required=True,
        help="Order quantity (base asset), e.g. 0.001",
    )
    parser.add_argument(
        "--price",
        help="Limit price (required for LIMIT orders)",
    )
    parser.add_argument(
        "--stop-price",
        help="Stop trigger price (required for STOP_MARKET orders)",
    )
    parser.add_argument(
        "--log-level", default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default: INFO)",
    )
    return parser


# --------------------------------------------------------------------------- #
#  Main                                                                        #
# --------------------------------------------------------------------------- #

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Re-initialise logger with the chosen level
    setup_logging(args.log_level)

    # Load credentials from environment (or .env file)
    api_key    = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        print(
            "\n❌  Error: BINANCE_API_KEY and BINANCE_API_SECRET must be set.\n"
            "   Create a .env file or export them as environment variables.\n"
        )
        sys.exit(1)

    client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret)

    try:
        place_order(
            client=client,
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValidationError as exc:
        print(f"\n❌  Validation error: {exc}\n")
        sys.exit(2)
    except BinanceAPIError as exc:
        print(f"\n❌  Binance API error [{exc.code}]: {exc.msg}\n")
        sys.exit(3)
    except (ConnectionError, TimeoutError) as exc:
        print(f"\n❌  Network error: {exc}\n")
        sys.exit(4)
    except Exception as exc:
        print(f"\n❌  Unexpected error: {exc}\n")
        logger.exception("Unexpected error")
        sys.exit(99)


if __name__ == "__main__":
    main()
