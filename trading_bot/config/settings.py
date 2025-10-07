# trading_bot/config/settings.py

# DhanHQ API credentials
# IMPORTANT: Do not hardcode your credentials here.
# Use environment variables or a secure vault in a real-world scenario.
DHAN_CLIENT_ID = "YOUR_CLIENT_ID"
DHAN_ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"

# Capital allocation for the strategy
TOTAL_CAPITAL = 100000  # Example: 1,00,000
RISK_PER_TRADE_PERCENT = 0.8 # 0.8% of total capital per trade