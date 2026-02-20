# Binance Futures Testnet Trading Bot

A clean, production-style Python CLI application that places **Market**, **Limit**, and **Stop-Market** orders on the Binance USDT-M Futures Testnet.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API wrapper (signing, requests, error handling)
│   ├── orders.py          # Order placement logic + result formatting
│   ├── validators.py      # Input validation (symbol, side, type, qty, price)
│   └── logging_config.py  # Rotating file + console logging setup
├── logs/
│   └── trading_bot.log    # Sample log output (auto-created on first run)
├── cli.py                 # CLI entry point (argparse)
├── .env.example           # Template for API credentials
├── requirements.txt
└── README.md
```

---

## Setup (Step-by-Step)

### 1. Prerequisites

- Python **3.9+** installed
- `git` installed (optional, for cloning)

### 2. Get Binance Futures Testnet Credentials

1. Visit [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Click **"Log In with GitHub"** (or register) and authorise access
3. After login, go to **"API Key"** tab on the dashboard
4. Click **"Generate Key"** — copy and save both the **API Key** and **Secret Key** immediately (the secret is shown only once)

### 3. Clone / Download the Project

```bash
git clone https://github.com/your-username/trading-bot.git
cd trading_bot
```

Or unzip the submitted archive and `cd` into the `trading_bot/` folder.

### 4. Create and Activate a Virtual Environment

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure API Credentials

```bash
# Copy the template
cp .env.example .env
```

Open `.env` in any text editor and fill in your credentials:

```dotenv
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
```

> ⚠️ Never commit `.env` to version control. It is already listed in `.gitignore`.

---

## How to Run

### Syntax

```bash
python cli.py --symbol SYMBOL --side BUY|SELL --type MARKET|LIMIT|STOP_MARKET \
              --quantity QTY [--price PRICE] [--stop-price STOP_PRICE]
```

### Examples

**Market BUY – buy 0.001 BTC at current market price**
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

**Market SELL – sell 0.01 ETH at current market price**
```bash
python cli.py --symbol ETHUSDT --side SELL --type MARKET --quantity 0.01
```

**Limit SELL – place a limit sell order at $70,000**
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000
```

**Limit BUY – place a limit buy order at $60,000**
```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 60000
```

**Stop-Market BUY (bonus) – triggers a market buy when price hits $68,000**
```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 68000
```

### Sample Output

```
──────────────────────────────────────────────────
  ORDER REQUEST SUMMARY
──────────────────────────────────────────────────
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.001
──────────────────────────────────────────────────
──────────────────────────────────────────────────
  ORDER RESPONSE
──────────────────────────────────────────────────
  Order ID       : 4751823
  Client OID     : x-Testnet-abc123
  Status         : FILLED
  Executed Qty   : 0.001
  Avg Price      : 67412.30
  Cumulative USD : 67.41230
──────────────────────────────────────────────────
  ✅  Order placed successfully!
```

---

## Logging

All activity is logged to **`logs/trading_bot.log`** automatically.

The log includes:
- Every API request URL and parameters (signature excluded)
- Full API response body
- Validation errors with details
- Network / timeout errors
- Unexpected exceptions with full stack traces

Log files rotate at 5 MB and keep 3 backups (`trading_bot.log.1`, `.2`, `.3`).

To increase verbosity (e.g., for debugging):
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --log-level DEBUG
```

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Missing required argument | argparse prints usage and exits with code 1 |
| Invalid symbol / side / type | `ValidationError` printed, exit code 2 |
| Missing price for LIMIT order | `ValidationError` printed, exit code 2 |
| Binance API rejects order | `BinanceAPIError` with code + message, exit code 3 |
| No internet / DNS failure | `ConnectionError` message, exit code 4 |
| Request timeout | `TimeoutError` message, exit code 4 |
| Missing API credentials in `.env` | Clear instruction printed, exit code 1 |

---

## Assumptions

- The bot targets **USDT-M Futures Testnet** only (`https://testnet.binancefuture.com`).
- `timeInForce` defaults to `GTC` (Good Till Cancelled) for LIMIT orders.
- Quantity precision must meet the exchange's filter rules (e.g., 0.001 for BTCUSDT). If you get a precision error from the API, adjust your `--quantity` accordingly.
- Testnet funds are virtual — no real money is involved.

---

## Bonus Feature

A third order type, **STOP_MARKET**, is supported via `--type STOP_MARKET --stop-price <price>`. This places a market order that triggers when the mark price crosses the specified stop price.

---

## Dependencies

| Package | Purpose |
|---|---|
| `requests` | HTTP client for Binance REST API |
| `python-dotenv` | Load API credentials from `.env` file |
