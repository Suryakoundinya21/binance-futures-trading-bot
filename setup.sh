#!/bin/bash
# ─────────────────────────────────────────────
#  Trading Bot — macOS Setup Script
#  Run once: bash setup.sh
# ─────────────────────────────────────────────
set -e

echo ""
echo "═══════════════════════════════════════════"
echo "  Binance Futures Testnet Bot — Setup"
echo "═══════════════════════════════════════════"

# 1. Create virtual environment
echo ""
echo "▶  Step 1/5 — Creating virtual environment..."
python3 -m venv venv
echo "   ✅ venv created"

# 2. Activate it
echo ""
echo "▶  Step 2/5 — Activating virtual environment..."
source venv/bin/activate
echo "   ✅ venv activated"

# 3. Upgrade pip silently
echo ""
echo "▶  Step 3/5 — Upgrading pip..."
pip install --upgrade pip --quiet
echo "   ✅ pip upgraded"

# 4. Install all dependencies (including certifi for SSL fix)
echo ""
echo "▶  Step 4/5 — Installing dependencies..."
pip install -r requirements.txt --quiet
echo "   ✅ requests, python-dotenv, certifi installed"

# 5. Create .env if it doesn't exist
echo ""
echo "▶  Step 5/5 — Setting up .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "   ✅ .env file created from template"
else
    echo "   ⚠️  .env already exists — skipping"
fi

echo ""
echo "═══════════════════════════════════════════"
echo "  ✅  Setup complete!"
echo "═══════════════════════════════════════════"
echo ""
echo "  NEXT STEPS:"
echo ""
echo "  1. Open .env and paste your Binance Testnet keys:"
echo "     nano .env"
echo ""
echo "  2. Activate the venv (every new terminal session):"
echo "     source venv/bin/activate"
echo ""
echo "  3. Place a Market order:"
echo "     python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001"
echo ""
echo "  4. Place a Limit order:"
echo "     python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000"
echo ""
echo "  5. Check logs:"
echo "     cat logs/trading_bot.log"
echo ""
