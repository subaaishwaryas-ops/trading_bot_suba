# Binance Futures Testnet Trading Bot

A clean, structured Python CLI application for placing orders on the **Binance Futures Testnet (USDT-M)**.
##  Technical Highlights

- *Financial Precision:* Uses the Decimal library for all quantity and price calculations to avoid floating-point errors common in financial applications.
- *Security-First:* Implements *HMAC SHA256* signature authentication. Credentials are never hardcoded and are managed via system environment variables.
- *Modular Architecture:* Follows a clear separation of concerns with dedicated layers for API communication, business logic (orders), and input validation.
- *Robust Validation:* Includes a comprehensive validation layer to catch input errors (invalid symbols, negative quantities, etc.) before they hit the API.
- *Advanced Logging:* Dual-stream logging to console (clean info) and local files (detailed debug data for troubleshooting).

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API client wrapper
│   ├── orders.py          # Order placement logic
│   ├── validators.py      # Input validation
│   └── logging_config.py  # Logging setup (file + console)
├── logs/                  # Auto-created; log files written here
├── cli.py                 # CLI entry point
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Get Testnet API Credentials

1. Visit [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in with GitHub and generate API Key + Secret from the dashboard.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables

**Windows (Command Prompt):**
```cmd
set BINANCE_API_KEY=your_api_key_here
set BINANCE_API_SECRET=your_api_secret_here
```

**Windows (PowerShell):**
```powershell
$env:BINANCE_API_KEY="your_api_key_here"
$env:BINANCE_API_SECRET="your_api_secret_here"
```

**Linux / macOS:**
```bash
export BINANCE_API_KEY=your_api_key_here
export BINANCE_API_SECRET=your_api_secret_here
```

---

## How to Run

### Place a MARKET order

```bash
python cli.py place --symbol BTCUSDT --type MARKET --side BUY --quantity 0.001
```

### Place a LIMIT order

```bash
python cli.py place --symbol BTCUSDT --type LIMIT --side SELL --quantity 0.001 --price 95000
```

### Place a STOP_MARKET order *(bonus order type)*

```bash
python cli.py place --symbol BTCUSDT --type STOP_MARKET --side SELL --quantity 0.001 --stop-price 85000
```

### View account summary

```bash
python cli.py account
```

### Help

```bash
python cli.py --help
python cli.py place --help
```

---

## Example Output

```
──────────────────────────────────────────────────
  ORDER REQUEST
──────────────────────────────────────────────────
  Symbol:             BTCUSDT
  Type:               MARKET
  Side:               BUY
  Quantity:           0.001

──────────────────────────────────────────────────
  ORDER RESPONSE
──────────────────────────────────────────────────
  Order ID:           4751830293
  Symbol:             BTCUSDT
  Status:             FILLED
  Side:               BUY
  Type:               MARKET
  Orig Qty:           0.001
  Executed Qty:       0.001
  Avg Price:          83421.50000

✔  Order placed successfully!
```

---

## Logging

Logs are written to `logs/trading_bot_YYYYMMDD.log` automatically.

- **Console**: INFO level and above
- **Log file**: Full DEBUG level (request params, responses, errors)

Sample log files for a MARKET and LIMIT order are included in `logs/`.

---

## Assumptions

- All orders are placed on **USDT-M Futures Testnet** (`https://testnet.binancefuture.com`).
- Credentials are provided via environment variables (not hardcoded for security).
- `timeInForce` defaults to `GTC` for LIMIT orders.
- Quantity precision must match the symbol's step size on testnet (e.g. 0.001 BTC minimum for BTCUSDT).
- The bonus third order type implemented is **STOP_MARKET** (stop-loss trigger order).

---

## Requirements

- Python 3.8+
- `requests` library (see `requirements.txt`)
